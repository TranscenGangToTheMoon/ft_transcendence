FROM        python:3.12.6-slim-bullseye

EXPOSE      8000

COPY        requirements.txt /
RUN         pip install -r requirements.txt

WORKDIR     /code

COPY        entrypoint.sh /
RUN         chmod u+x /entrypoint.sh

ENTRYPOINT  ["/entrypoint.sh"]
CMD         ["python", "manage.py", "runserver", "0.0.0.0:8000"]
