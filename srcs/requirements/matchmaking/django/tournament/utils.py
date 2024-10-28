from rest_framework import serializers

from matchmaking.request import requests_game, ServiceUnavailable
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


def get_user_participant(tournament, user_id, creator_check=False):
    kwargs = {'user_id': user_id}
    if tournament is not None:
        kwargs['tournament'] = tournament.id

    try:
        p = TournamentParticipants.objects.get(**kwargs)
        if creator_check and not p.creator:
            raise serializers.ValidationError({'detail': 'You are not creator of this tournament.'})
        return p
    except TournamentParticipants.DoesNotExist:
        if tournament is None:
            raise serializers.ValidationError({'detail': 'You are not in any tournament.'})
        raise serializers.ValidationError({'detail': 'You are not participant of this tournament.'})
