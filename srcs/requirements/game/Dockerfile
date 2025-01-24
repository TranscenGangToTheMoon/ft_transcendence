##### Base build
FROM python:3.13.0-slim AS base

EXPOSE 8000

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y postgresql-client

COPY init.d /init.d

RUN pip install --no-cache-dir -r /init.d/requirements.txt
RUN chmod u+x /init.d/entrypoint.sh

WORKDIR /code

##### Development build
FROM base AS development

RUN apt-get install -y --no-install-recommends curl net-tools

ENTRYPOINT ["/init.d/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

##### Production build
FROM base AS production

COPY django /code

RUN pip install daphne

ENTRYPOINT ["/init.d/entrypoint.sh"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "game.asgi:application"]
