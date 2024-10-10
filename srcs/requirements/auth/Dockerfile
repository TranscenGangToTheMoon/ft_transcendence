FROM        python:3.12.6-slim-bullseye
LABEL       authors="basil"

EXPOSE      8000

WORKDIR     /code

COPY        ../install_django.sh /
RUN         chmod u+x /install_django.sh

ENTRYPOINT  ["/install_django.sh"]
