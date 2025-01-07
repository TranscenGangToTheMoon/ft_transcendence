#!/bin/bash
RED="\001\033[031m\002"
BOLD="\001\033[001m\002"
RESET="\001\033[000m\002"

# sleep 20
pip install -e /shared/ # todo remove in prod

echo -e $BOLD$RED"- Matchmaking migrations processing"$RESET

if [[ $MIGRATION = true ]]; then
    echo -e $BOLD$RED"- Making migrations"$RESET
    python manage.py makemigrations
fi
echo -e $BOLD$RED"- Migrating"$RESET
python manage.py migrate

PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p 5432 -U $POSTGRES_USER -d $POSTGRES_DB -c "
DELETE FROM baning_banned;
DELETE FROM blocking_blocked;
DELETE FROM lobby_lobby;
DELETE FROM lobby_lobbyparticipants;
DELETE FROM play_players;
DELETE FROM tournament_tournament;
DELETE FROM tournament_tournamentstage;
DELETE FROM tournament_tournamentparticipants;
DELETE FROM tournament_tournamentmatches;
"

exec "$@"