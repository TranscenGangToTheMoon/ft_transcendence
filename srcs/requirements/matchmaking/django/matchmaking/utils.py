from typing import Literal

from lib_transcendence.services import requests_game, requests_users
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, NotFound

from lobby.models import Lobby, LobbyParticipants
from play.models import Players
from tournament.models import Tournaments, TournamentParticipants


# -------------------- GET PARTICIPANT ------------------------------------------------------------------------------- #
def get_participant(name: Literal['lobby', 'tournament'], model, obj, user_id, creator_check, from_place):
    kwargs = {'user_id': user_id}
    if obj is not None:
        kwargs[name] = obj.id

    try:
        p = model.objects.get(**kwargs)
        if creator_check and not p.creator:
            raise PermissionDenied(f'You are not creator of this {name}.')
        return p
    except model.DoesNotExist:
        if from_place:
            raise NotFound(f'You are not in any {name}.')
        raise NotFound(f'You do not belong to this {name}.')


def get_lobby_participant(lobby, user_id, creator_check=False, from_place=False):
    return get_participant('lobby', LobbyParticipants, lobby, user_id, creator_check, from_place)


def get_tournament_participant(tournament, user_id, creator_check=False, from_place=False):
    return get_participant('tournament', TournamentParticipants, tournament, user_id, creator_check, from_place)


def get_kick_participants(name: Literal['lobby', 'tournament'], model, user_id):
    try:
        return model.participants.get(user_id=user_id)
    except LobbyParticipants.DoesNotExist:
        raise NotFound(f'This user does not belong to this {name}.')


# -------------------- GET PLACE ------------------------------------------------------------------------------------- #
def get_place(name: Literal['lobby', 'tournament'], model, create, **kwargs):
    allowed_keys = ('id', 'code')

    key = list(kwargs)[0]
    assert len(kwargs) == 1 and key in allowed_keys

    value = kwargs[key]
    if value is None:
        raise serializers.ValidationError({key: [f'{name.title()} {key} is required.']})
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        if create:
            raise NotFound({'code': [f'{name.title()} code does not exist.']})
        raise NotFound(f'You do not belong to this {name}.')


def get_lobby(code, create=False):
    return get_place('lobby', Lobby, create, code=code)


def get_tournament(create=False, **kwargs):
    return get_place('tournament', Tournaments, create, **kwargs)


# -------------------- GET PARTICIPANT ------------------------------------------------------------------------------- #
# todo move to library
def create_match(tournament_id, stage_id, teams):
    data = {
        'tournament_id': tournament_id,
        'tournament_stage_id': stage_id,
        'game_mode': 'tournament',
        'teams': teams
    }

    requests_game('match/', data=data)


# -------------------- VERIFY USER ----------------------------------------------------------------------------------- #
def verify_user(user_id, join_tournament=True):
    try:
        participant = TournamentParticipants.objects.get(user_id=user_id, still_in=True)
        if participant.creator:
            if join_tournament:
                raise PermissionDenied('You are already in a tournament.')
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


# -------------------- BLOCK CHECK ----------------------------------------------------------------------------------- #
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
