FROM python:3.12.6-slim
LABEL authors="basil"

EXPOSE 8000

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y --no-install-recommends curl net-tools libpq-dev

COPY        requirements.txt /
RUN         pip install -r requirements.txt

WORKDIR     /code

# RUN       daphne game.asgi:application

COPY        entrypoint.sh /
RUN         chmod u+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
