FROM        python:3.12.6-slim-bullseye
LABEL       authors="basil"

EXPOSE      8000

WORKDIR     /code

COPY        tools/install_django.sh /
RUN         chmod u+x /start_django.sh

ENTRYPOINT  ["/start_django.sh"]
