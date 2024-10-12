#!/bin/bash

pip install --root-user-action -r requirements.txt
cd ./srcs/
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
