from typing import Literal

from lib_transcendence import endpoints
from lib_transcendence.exceptions import MessagesException, Conflict
from lib_transcendence.services import request_game, request_users
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, NotFound, APIException

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
            raise PermissionDenied(MessagesException.PermissionDenied.NOT_CREATOR.format(obj=name))
        return p
    except model.DoesNotExist:
        if from_place:
            raise NotFound(MessagesException.NotFound.NOT_BELONG.format(obj=name))
        raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG.format(obj=name))


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
        raise serializers.ValidationError({key: [MessagesException.ValidationError.REQUIRED.format(obj=f'{name.title()} {key}')]})
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        if create:
            raise NotFound(MessagesException.NotFound.NOT_FOUND.format(obj=name.title()))
        raise NotFound(MessagesException.PermissionDenied.NOT_BELONG.format(obj=name))


def get_lobby(code, create=False):
    return get_place('lobby', Lobby, create, code=code)


def get_tournament(create=False, **kwargs):
    return get_place('tournament', Tournaments, create, **kwargs)


# -------------------- CREATE MATCH ---------------------------------------------------------------------------------- #
# todo move to library
def create_match(tournament_id, stage_id, teams):
    data = {
        'tournament_id': tournament_id,
        'tournament_stage_id': stage_id,
        'game_mode': 'tournament',
        'teams': teams
    }

    requests_game('match/', data=data)


# -------------------- GET PARTICIPANT ------------------------------------------------------------------------------- #
def kick_yourself(user_id, kick_user_id):
    if user_id == kick_user_id:
        raise PermissionDenied(MessagesException.PermissionDenied.KICK_YOURSELF)


# -------------------- VERIFY USER ----------------------------------------------------------------------------------- #
def verify_user(user_id, join_tournament=True):
    try:
        participant = TournamentParticipants.objects.get(user_id=user_id, still_in=True)
        if join_tournament and participant.tournament.is_started:
            raise Conflict(MessagesException.Conflict.ALREADY_IN_TOURNAMENT)
        if participant.creator:
            raise PermissionDenied(MessagesException.PermissionDenied.CAN_CREATE_MORE_THAN_ONE_TOURNAMENT)
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
        raise Conflict(MessagesException.Conflict.USER_ALREADY_IN_GAME)
        request_game(endpoints.Game.fmatch_user.format(user_id=user_id), method='GET')
    except NotFound:
        pass


# -------------------- BLOCK CHECK ----------------------------------------------------------------------------------- #
def can_join(request, obj, new_user):
    try:
        self_user = obj.participants.get(creator=True).user_id
    except obj.DoesNotExist:
        raise NotFound(MessagesException.NotFound.CREATOR)

    try:
        return False
        request_users(endpoints.Users.fare_blocked.format(user1_id=self_user, user2_id=new_user), 'GET', request)
    except NotFound:
        return True
    except APIException: #todo handle
        raise PermissionDenied('You cannot join this lobby.')
