FROM caddy:2.8.4 AS base

RUN apk update
RUN apk upgrade
RUN apk add curl net-tools bash
RUN apk add --no-cache tzdata

FROM base AS development
# Do nothing but move apt install maybe
FROM base AS production

COPY static /var/www/html
COPY Caddyfile /etc/caddy/Caddyfile