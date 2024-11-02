from typing import Literal

from lib_transcendence.services import requests_game
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from lobby.models import LobbyParticipants
from play.models import Players
from tournament.models import TournamentParticipants


def get_participants(name: Literal['lobby', 'tournament'], model, obj, user_id, creator_check):
    kwargs = {'user_id': user_id}
    if obj is not None:
        kwargs[name] = obj.id

    try:
        p = model.objects.get(**kwargs)
        if creator_check and not p.creator:
            raise serializers.ValidationError({'detail': f'You are not creator of this {name}.'})
        return p
    except model.DoesNotExist:
        if obj is None:
            raise serializers.ValidationError({'detail': f'You are not in any {name}.'})
        raise serializers.ValidationError({'detail': f'You are not participant of this {name}.'})


def verify_user(user_id, join_tournament=True):
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
