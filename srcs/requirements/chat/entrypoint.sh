#!/bin/bash

# sleep 20 too loooooong # todo Replace with a healthcheck
python manage.py makemigrations
python manage.py migrate

exec "$@"
