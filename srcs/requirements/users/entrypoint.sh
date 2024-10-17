#!/bin/bash

sleep 5 # Replace with a healthcheck
python manage.py makemigrations
python manage.py migrate

exec "$@"