const prerender = require("prerender");
const { getLogger } = require("./logging");

const log = getLogger("main");
ENABLED_PLUGINS =
  (process.env.ENABLED_PLUGINS && process.env.ENABLED_PLUGINS.split(",")) || [];
PLUGINS = {
  addMetaTags: prerender.addMetaTags,
  basicAuth: prerender.basicAuth,
  blacklist: prerender.blacklist,
  // We use a fixed version of `blockResources`. Details: <https://github.com/prerender/prerender/pull/778>
  blockResources: () => {
    return require("./blockResources");
  },
  browserForceRestart: prerender.browserForceRestart,
  fscache: () => {
    return require("prerender-plugin-fscache");
  },
  httpHeaders: prerender.httpHeaders,
  removeScriptTags: prerender.removeScriptTags,
  sendPrerenderHeader: prerender.sendPrerenderHeader,
  whitelist: prerender.whitelist,
};

const server = prerender({
  chromeLocation: "/usr/bin/chromium",
  chromeFlags: [
    "--no-sandbox",
    "--headless",
    "--disable-gpu",
    "--remote-debugging-port=9222",
    "--remote-debugging-address=127.0.0.1",
    "--hide-scrollbars",
    "--blink-settings=imagesEnabled=false",
    "--disable-dev-shm-usage", // Avoid `net::ERR_INSUFFICIENT_RESOURCES`
  ],
  logRequests: process.env.PRERENDER_LOG_REQUESTS === "true",
  port: process.env.PORT || 3000,
  browserDebuggingPort: 9222,
});

for (let plugin of ENABLED_PLUGINS) {
  if ((!plugin) in PLUGINS) {
    process.stderr.write(`ERROR: plugin ${plugin} not found.`);
    process.exit(1);
  }
  log(`Enabling plugin ${plugin}`);
  server.use(PLUGINS[plugin]());
}
server.start();
