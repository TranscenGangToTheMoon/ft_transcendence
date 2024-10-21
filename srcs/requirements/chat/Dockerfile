FROM python:3.13.0-slim
LABEL authors="basil"

EXPOSE 8000

RUN apt-get update
RUN apt-get upgrade
RUN apt-get install -y --no-install-recommends curl net-tools

COPY /django/requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /code

COPY entrypoint.sh /
RUN chmod u+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]