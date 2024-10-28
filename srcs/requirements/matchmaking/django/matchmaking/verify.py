from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from lobby.models import LobbyParticipants
from matchmaking.request import requests_game
from play.models import Players
from tournament.models import TournamentParticipants


def verify(user_id, join_tournament=True):
    try:
        participant = TournamentParticipants.objects.get(user_id=user_id, still_in=True)
        if participant.creator:
            if join_tournament:
                raise serializers.ValidationError({'detail': 'You already join a tournament.'})
            raise serializers.ValidationError({'detail': 'You cannot create more than one tournament at the same time.'})
        participant.delete()
    except TournamentParticipants.DoesNotExist:
        pass

    try:
        Players.objects.get(user_id=user_id).delete()
    except Players.DoesNotExist:
        pass

    try:
        LobbyParticipants.objects.get(user_id=user_id).delete()
    except LobbyParticipants.DoesNotExist:
        pass

    try:
        requests_game(f'playing/{user_id}/', method='GET')
        raise serializers.ValidationError({'detail': 'You are already in a game.'})
    except AuthenticationFailed as e:
        if e.detail.get('detail') != 'Not found.': # todo in library
            raise e
