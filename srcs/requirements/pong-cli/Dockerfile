##### Base build
FROM debian:latest AS base

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install --no-install-recommends -y g++ make cmake libncurses5-dev git

COPY init.d /init.d

RUN chmod u+x /init.d/entrypoint.sh
##### Development build
FROM base AS development

RUN apt-get install -y --no-install-recommends curl net-tools

ENTRYPOINT ["/init.d/entrypoint.sh"]
CMD ["sleep infinity"]

##### Production build
FROM base AS production

ENTRYPOINT ["/init.d/entrypoint.sh"]
CMD ["sleep infinity"]
