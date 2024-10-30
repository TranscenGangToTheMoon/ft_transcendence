from rest_framework import serializers

from lib-transcendence.services import requests_game
from matchmaking.utils import get_participants
from tournament.models import Tournaments, TournamentParticipants


def create_match(tournament_id, stage_id, teams):
    data = {
        'tournament_id': tournament_id,
        'tournament_stage_id': stage_id,
        'game_mode': 'tournament',
        'teams': teams
    }

    requests_game('match/', data=data)


def get_tournament(**kwargs):
    allowed_keys = ('id', 'code')

    key = list(kwargs)[0]
    assert len(kwargs) == 1 and key in allowed_keys

    value = kwargs[key]
    if value is None:
        raise serializers.ValidationError({'detail': f'Tournament {key} is required.'})
    try:
        return Tournaments.objects.get(**kwargs)
    except Tournaments.DoesNotExist:
        raise serializers.ValidationError({'detail': f"Tournament '{value}' does not exist."})


def get_tournament_participants(tournament, user_id, creator_check=False):
    return get_participants('tournament', TournamentParticipants, tournament, user_id, creator_check)
