# dokku-prerender

This repository has a `Dockerfile` and instructions for running [prerender](https://github.com/prerender/prerender) on
[Dokku](https://dokku.com/). You can easily enable official plugins (including a fixed version of `blockRequests`) and
our [prerender-plugin-fscache](https://www.npmjs.com/package/prerender-plugin-fscache).

Note that pre-rendering is NOT the same as server-side rendering: pre-rendering just helps you get better SEO by
serving a pre-rendered HTML version with data filled in, but it's not supposed to replace the user experience in the
browser. To make it work you'll need:
- A deployed prerender (this repository will help you deploy it to Dokku)
- Change your website configuration to serve static files to regular users but reverse proxy to your prerender instance
  when the user-agent is from a search engine or social media robot (see [Configuring Nginx](#configuring-nginx) for an
  example)

Run on your Dokku server:

```shell
# Change these variables as needed
ADMIN_EMAIL="admin@example.net"
APP_DOMAIN="prerender.example.net"
APP_NAME="myprerender"
ALLOWED_DOMAINS="example.net"  # Change if needed (like has other domains/subdomains)
ENABLED_PLUGINS="addMetaTags,blockResources,browserForceRestart,fscache,removeScriptTags,whitelist"
STORAGE_PATH="/var/lib/dokku/data/storage/$APP_NAME"  # Data path on host machine for caching
CACHE_PATH="/var/cache/prerender"  # Data path inside container for caching
CACHE_STATUS_CODES="200,301,302,303,304,307,308,404"  # Status codes where cache works (only GET requests are cached)
CACHE_TTL="86400"  # Cache time-to-live (in seconds)

dokku apps:create $APP_NAME
dokku domains:set $APP_NAME $APP_DOMAIN
dokku storage:ensure-directory --chown heroku $APP_NAME
dokku storage:mount $APP_NAME "$STORAGE_PATH:$CACHE_PATH"
dokku letsencrypt:set $APP_NAME email $ADMIN_EMAIL

# Now, let's go to the prerender/plugin-specific env vars:
dokku config:set --no-restart $APP_NAME ALLOWED_DOMAINS=$ALLOWED_DOMAINS # Only if you'd like to enable domain allow list
dokku config:set --no-restart $APP_NAME CACHE_PATH=$CACHE_PATH # Only if you'd like to enable cache
dokku config:set --no-restart $APP_NAME CACHE_TTL=$CACHE_TTL # Only if you'd like to enable cache
dokku config:set --no-restart $APP_NAME ENABLED_PLUGINS=$ENABLED_PLUGINS
dokku config:set --no-restart $APP_NAME CACHE_STATUS_CODES=$CACHE_STATUS_CODES
```

> Note that prerender reads some environment variables and you can set them with
> `dokku config:set $APP_NAME VAR=value`. See the list of plugins in the section [Available
> Plugins](#available-plugins) and the file system cache plugin environment variables in [Cache
> settings](#cache-settings).

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


## Running locally

```shell
cp env.example .env
make start # or: `docker compose build && docker compose up -d`
```

Now, access [http://localhost:3000/https://example.net/](http://localhost:3000/https://example.net/).


## Available Plugins

- `addMetaTags`: Add `x-prerender-render-id` and `x-prerender-render-at` meta tags with debugging info
- `basicAuth`: Requires HTTP auth (using `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD`)
- `blacklist`: Block domains from `BLACKLISTED_DOMAINS`
- `blockResources`: Ignore requests of images, fonts and to some domains (like Google Analytics)
- `browserForceRestart`: Restart browser after `BROWSER_FORCE_RESTART_PERIOD` milliseconds (default: `3600000`)
- `fscache`: cache GET responses on filesystem. Only some status codes (`CACHE_STATUS_CODES`) are cached. Files
  are stored at `CACHE_PATH` and expires after `CACHE_TIMEOUT` seconds
- `httpHeaders`: Transform `prerender-status-code` and `prerender-header` meta tags into response headers
- `removeScriptTags`: Remove `<script>` (except for type='application/ld+json') and `<link rel="import">` tags
- `sendPrerenderHeader`: Add `X-Prerender: 1` to request headers
- `whitelist`: Render only pages from domains in `ALLOWED_DOMAINS`


## Utilities

The directory `utils` has some useful Python scripts:

- `warmup_cache.py`: from a prerender instance URL and a text file with URLs, this script will request all these URLs
  to the prerender server, so you end up with all of them cached.
- `refresh_facebook_cache.py`: scrape [Facebook Share Debugger](https://developers.facebook.com/tools/debug/) to
  refresh URLs from a text file. Will help creating previews when people share your links.


## Configuring Nginx

If you're serving your static file on Nginx, you'll need to configure it to proxy the robot requests through your
prerender instance. Check the file [nginx-default.conf](nginx-default.conf) for an example (I curated a list of 68
robots, including search engines, social media and SEO metrics).
