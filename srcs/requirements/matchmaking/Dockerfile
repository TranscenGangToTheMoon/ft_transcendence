FROM        python:3.12.6-slim-bullseye

EXPOSE      8000

COPY        requirements.txt /
RUN         pip install -r requirements.txt

WORKDIR     /code

ENTRYPOINT  ["python", "manage.py"]
CMD         ["runserver", "0.0.0.0:8000"]
