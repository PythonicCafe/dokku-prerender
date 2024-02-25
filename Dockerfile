FROM node:21-bookworm

RUN apt update \
  && apt install -y chromium \
  && apt upgrade -y \
  && apt purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt clean \
  && rm -rf /var/lib/apt/lists/*
RUN yarn add pm2 chrome-remote-interface@0.33.0 prerender@5.20.2 prerender-plugin-fscache@1.0.1
RUN mkdir -p /app && chown -R node:node /app

USER node
WORKDIR /app
COPY . /app/
CMD ["yarn", "pm2-runtime", "start", "/app/server.js"]
