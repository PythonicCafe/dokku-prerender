const prerender = require('prerender');

function log(...args) {
  if (process.env.DISABLE_LOGGING) {
    return;
  }
  console.log(new Date().toISOString(), ...args);
}

ENABLED_PLUGINS = (process.env.ENABLED_PLUGINS && process.env.ENABLED_PLUGINS.split(',')) || [];
PLUGINS = {
  addMetaTags: prerender.addMetaTags,
  basicAuth: prerender.basicAuth,
  blacklist: prerender.blacklist,
  blockResources: prerender.blockResources,
  browserForceRestart: prerender.browserForceRestart,
  httpHeaders: prerender.httpHeaders,
  removeScriptTags: prerender.removeScriptTags,
  sendPrerenderHeader: prerender.sendPrerenderHeader,
  whitelist: prerender.whitelist,
}

const server = prerender(
  {
    chromeLocation: '/usr/bin/chromium',
    chromeFlags: [
      '--no-sandbox',
      '--headless',
      '--disable-gpu',
      '--remote-debugging-port=9222',
      '--hide-scrollbars',
      '--blink-settings=imagesEnabled=false',
      '--disable-dev-shm-usage', // Avoid `net::ERR_INSUFFICIENT_RESOURCES`
    ],
    logRequests: true,
  }
);
for (let plugin of ENABLED_PLUGINS) {
  if (!plugin in PLUGINS) {
    process.stderr.write(`ERROR: plugin ${plugin} not found.`)
    process.exit(1);
  }
  log(`Enabling plugin ${plugin}`)
  server.use(PLUGINS[plugin]());
}
server.start();