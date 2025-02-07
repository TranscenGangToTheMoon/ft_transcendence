##### Base build
FROM caddy:2.8.4 AS base

RUN apk update
RUN apk upgrade
RUN apk add --no-cache tzdata

##### Development build
FROM base AS development
RUN apk add curl net-tools bash

##### Production build
FROM base AS production

COPY static /var/www/html
COPY Caddyfile-prod/Caddyfile /etc/caddy/Caddyfile

##### VPS build
FROM base AS vps

COPY static /var/www/html
COPY Caddyfile-vps/Caddyfile /etc/caddy/Caddyfile