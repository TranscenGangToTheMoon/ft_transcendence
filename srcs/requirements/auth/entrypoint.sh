#!/bin/bash

sleep 20 # todo Replace with a healthcheck
python manage.py makemigrations
python manage.py migrate

exec "$@"
