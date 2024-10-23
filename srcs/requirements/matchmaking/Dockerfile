FROM python:3.12.6-slim
LABEL authors="basil"

EXPOSE 8000

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y --no-install-recommends curl net-tools

COPY /django/requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /code

# COPY entrypoint.sh /
# RUN chmod u+x /entrypoint.sh
# RUN daphne -b 0.0.0.0 -p 8000 matchmaking.asgi:application

# ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
