#!/bin/bash
RED="\001\033[031m\002"
BOLD="\001\033[001m\002"
RESET="\001\033[000m\002"

pip install -e /shared/ # todo remove in prod

echo -e $BOLD$RED"- Game migrations processing"$RESET

if [[ $MIGRATION = true ]]; then
    echo -e $BOLD$RED"- Making migrations"$RESET
    python manage.py makemigrations
fi
echo -e $BOLD$RED"- Migrating"$RESET
python manage.py migrate

PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p 5432 -U $POSTGRES_USER -d $POSTGRES_DB -c "
DELETE FROM matches_players WHERE match_id IN (SELECT id FROM matches_matches WHERE finished = FALSE);
DELETE FROM matches_teams WHERE match_id IN (SELECT id FROM matches_matches WHERE finished = FALSE);
DELETE FROM matches_matches WHERE finished = FALSE;
"

GAME_MAX_SCORE=$(jq '.score.max' 'game_server/gameConfig.json')
export GAME_MAX_SCORE

python socket_server.py &

exec "$@"
