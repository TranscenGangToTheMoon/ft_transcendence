#!/bin/bash

sleep 2
python -m pip install /shared/ # todo remove in prod
python manage.py makemigrations
python manage.py migrate

exec "$@"
