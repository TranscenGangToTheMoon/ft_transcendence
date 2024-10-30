#!/bin/bash

python manage.py makemigrations
python manage.py migrate
python -m pip install -e /shared/

exec "$@"
