#!/bin/bash
RED="\001\033[031m\002"
BOLD="\001\033[001m\002"
RESET="\001\033[000m\002"

sleep 25
pip install -e /shared/ # todo remove in prod

echo -e $BOLD$RED"- Users migrations processing"$RESET

if [[ $MIGRATION = true ]]; then
    echo -e $BOLD$RED"- Making migrations"$RESET
    python manage.py makemigrations
fi
echo -e $BOLD$RED"- Migrating"$RESET
python manage.py migrate

exec "$@"