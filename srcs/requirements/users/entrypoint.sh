#!/bin/bash

sleep 20
python manage.py makemigrations
python manage.py migrate

exec "$@"
