FROM python:3.12.6-slim-bullseye
LABEL authors="basil"

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

# RUN daphne game.asgi:application

EXPOSE 8000

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
