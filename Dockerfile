FROM node:21-bookworm

RUN apt update \
  && apt install -y chromium \
  && apt upgrade -y \
  && apt purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt clean \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app && chown -R node:node /app
WORKDIR /app
USER node

COPY package.json yarn.lock /app/
RUN cd /app && yarn install

COPY . /app/
CMD ["yarn", "run", "pm2-runtime", "start", "/app/server.js"]
