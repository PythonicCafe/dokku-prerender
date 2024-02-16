# dokku-prerender

This repository has a `Dockerfile` and instructions for running [prerender](https://github.com/prerender/prerender) on
[Dokku](https://dokku.com/).

Run on your Dokku server:

```shell
# Change these variables as needed
ADMIN_EMAIL="admin@example.net"
APP_DOMAIN="prerender.example.net"
APP_NAME="myprerender"
ALLOWED_DOMAINS=$APP_DOMAIN  # Change if needed (like has other domains/subdomains)
ENABLED_PLUGINS="addMetaTags,blockResources,browserForceRestart,httpHeaders,removeScriptTags,sendPrerenderHeader,whitelist"

dokku apps:create $APP_NAME
dokku domains:set $APP_NAME $APP_DOMAIN
dokku letsencrypt:set $APP_NAME email $ADMIN_EMAIL

# Now, let's go to the prerender/plugin-specific env vars:
dokku config:set --no-restart $APP_NAME ALLOWED_DOMAINS=$ALLOWED_DOMAINS  # Only if you'd like to enable domain allow list
```

> Note that prerender reads some environment variables and you can set them with
> `dokku config:set $APP_NAME VAR=value`. See the list of plugins in the section [Available
> Plugins](#available-plugins).

Now, clone this repository on your local machine, add the Dokku host as a remote and push to it:

```shell
git clone https://github.com/PythonicCafe/dokku-prerender.git
cd dokku-prerender
git remote add dokku dokku@<server-ip>:<app-name>
git push dokku main
```

Finally, activate Let's Encrypt by executing on the server:

```shell
dokku letsencrypt:enable $APP_NAME
```


## Available plugins

- `addMetaTags`: Add `x-prerender-render-id` and `x-prerender-render-at` meta tags with debugging info
- `basicAuth`: Requires HTTP auth (using `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD`)
- `blacklist`: Block domains from `BLACKLISTED_DOMAINS`
- `blockResources`: Ignore requests of images, fonts and to some domains (like Google Analytics)
- `browserForceRestart`: Restart browser after `BROWSER_FORCE_RESTART_PERIOD` milliseconds (default: `3600000`)
- `httpHeaders`: Transform `prerender-status-code` and `prerender-header` meta tags into response headers
- `removeScriptTags`: Remove `<script>` (except for type='application/ld+json') and `<link rel="import">` tags
- `sendPrerenderHeader`: Add `X-Prerender: 1` to request headers
- `whitelist`: Render only pages from domains in `ALLOWED_DOMAINS`
