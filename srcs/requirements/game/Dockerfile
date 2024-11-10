FROM python:3.13.0-slim

EXPOSE 8000

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y --no-install-recommends curl net-tools

COPY requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /code

# RUN       daphne game.asgi:application

COPY entrypoint.sh /
RUN chmod u+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]