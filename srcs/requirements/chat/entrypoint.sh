#!/bin/bash

sleep 10
python -m pip install -e /shared/ # todo remove in prod
python manage.py makemigrations
python manage.py migrate

exec "$@"
