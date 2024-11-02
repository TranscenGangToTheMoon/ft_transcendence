#!/bin/bash

sleep 20
python -m pip install /shared/ # todo remove in prod
python manage.py makemigrations
python manage.py migrate

exec "$@"
