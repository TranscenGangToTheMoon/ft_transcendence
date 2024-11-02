#!/bin/bash

python -m pip install -e /shared/
python manage.py makemigrations
python manage.py migrate

exec "$@"
