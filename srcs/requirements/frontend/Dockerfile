##### Base build
FROM caddy:2.8.4 AS base

RUN apk update -y
RUN apk upgrade -y
RUN apk add --no-cache tzdata

##### Development build
FROM base AS development
RUN apk add curl net-tools bash

##### Production build
FROM base AS production

COPY static /var/www/html
COPY Caddyfile /etc/caddy/Caddyfile

# WORKDIR /srv

# CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]