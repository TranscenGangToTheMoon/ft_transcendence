from typing import Literal

from lib_transcendence.services import requests_game, requests_users
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, NotFound

from lobby.models import Lobby, LobbyParticipants
from play.models import Players
from tournament.models import Tournaments, TournamentParticipants


def get_participants(name: Literal['lobby', 'tournament'], model, obj, user_id, creator_check):
    kwargs = {'user_id': user_id}
    if obj is not None:
        kwargs[name] = obj.id

    try:
        p = model.objects.get(**kwargs)
        if creator_check and not p.creator:
            raise PermissionDenied(f'You are not creator of this {name}.')
        return p
    except model.DoesNotExist:
        if obj is None:
            raise NotFound(f'You are not in any {name}.')
        raise NotFound(f'You are not a participant of this {name}.')


def verify_user(user_id, join_tournament=True):
    try:
        participant = TournamentParticipants.objects.get(user_id=user_id, still_in=True)
        if participant.creator:
            if join_tournament:
                raise PermissionDenied('You already join a tournament.')
            raise PermissionDenied('You cannot create more than one tournament at the same time.')
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
        raise PermissionDenied('You are already in a game.')
    except NotFound:
        pass


def can_join(request, obj, new_user):
    try:
        self_user = obj.participants.get(creator=True).user_id
    except obj.DoesNotExist:
        raise NotFound('Creator not found.')

    try:
        requests_users(request, f'block/{self_user}/{new_user}/', 'GET')
        return False
    except NotFound:
        return True
