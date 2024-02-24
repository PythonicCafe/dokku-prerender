FROM node:21-bookworm

WORKDIR /app

RUN apt update \
  && apt install -y chromium \
  && apt upgrade -y \
  && apt purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt clean \
  && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /app && chown -R node:node /app
RUN yarn add pm2 prerender prerender-plugin-fscache

USER node
COPY . /app/
CMD ["yarn", "pm2-runtime", "start", "/app/server.js"]
