from lib_transcendence.game import GameMode
from lib_transcendence import endpoints
from lib_transcendence.exceptions import MessagesException, Conflict, ResourceExists, ServiceUnavailable
from lib_transcendence.services import request_game, request_users
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, NotFound, APIException

from lobby.models import Lobby, LobbyParticipants
from play.models import Players
from tournament.models import Tournaments, TournamentParticipants


# -------------------- GET PARTICIPANT ------------------------------------------------------------------------------- #
def get_participant(model, obj, user_id, creator_check, from_place):
    kwargs = {'user_id': user_id}
    if obj is not None:
        kwargs[model.str_name] = obj.id

    try:
        p = model.objects.get(**kwargs)
        if creator_check and not p.creator:
            raise PermissionDenied(MessagesException.PermissionDenied.NOT_CREATOR.format(obj=model.str_name))
        return p
    except model.DoesNotExist:
        if from_place:
            raise NotFound(MessagesException.NotFound.NOT_BELONG.format(obj=model.str_name))
        raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG.format(obj=model.str_name))


def get_lobby_participant(lobby, user_id, creator_check=False, from_place=False):
    return get_participant(LobbyParticipants, lobby, user_id, creator_check, from_place)


def get_tournament_participant(tournament, user_id, creator_check=False, from_place=False):
    return get_participant(TournamentParticipants, tournament, user_id, creator_check, from_place)


def get_kick_participants(model, user_id):
    try:
        return model.participants.get(user_id=user_id)
    except (LobbyParticipants.DoesNotExist, TournamentParticipants.DoesNotExist):
        raise NotFound(f'This user does not belong to this {model.str_name}.')


# -------------------- GET PLACE ------------------------------------------------------------------------------------- #
def get_place(model, create, **kwargs):
    allowed_keys = ('id', 'code')

    key = list(kwargs)[0]
    assert len(kwargs) == 1 and key in allowed_keys

    value = kwargs[key]
    if value is None:
        raise serializers.ValidationError({key: [MessagesException.ValidationError.REQUIRED.format(obj=f'{model.str_name.title()} {key}')]})
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        if create:
            raise NotFound(MessagesException.NotFound.NOT_FOUND.format(obj=model.str_name.title()))
        raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG.format(obj=model.str_name))


def get_lobby(code, create=False):
    return get_place(Lobby, create, code=code)


def get_tournament(create=False, **kwargs):
    return get_place(Tournaments, create, **kwargs)


def verify_place(user, model, request):
    if are_users_blocked(request, model, user['id']):
        raise NotFound(MessagesException.NotFound.NOT_FOUND.format(obj=model.str_name.title()))

    if model.participants.filter(user_id=user['id']).exists():
        raise ResourceExists(MessagesException.ResourceExists.JOIN.format(obj=model.str_name))

    if model.str_name == GameMode.tournament and model.is_started:
        raise PermissionDenied(MessagesException.PermissionDenied.TOURNAMENT_ALREADY_STARTED)

    verify_user(user['id'])

    if model.is_full:
        raise PermissionDenied(MessagesException.PermissionDenied.IS_FULL.format(obj=model.str_name.title()))


# -------------------- GET PARTICIPANT ------------------------------------------------------------------------------- #
def kick_yourself(user_id, kick_user_id):
    if user_id == kick_user_id:
        raise PermissionDenied(MessagesException.PermissionDenied.KICK_YOURSELF)


# -------------------- VERIFY USER ----------------------------------------------------------------------------------- #
def verify_user(user_id, created_tournament=False):
    try:
        participant = TournamentParticipants.objects.get(user_id=user_id, still_in=True)
        if participant.tournament.is_started:
            raise Conflict(MessagesException.Conflict.ALREADY_IN_TOURNAMENT)
        if created_tournament and participant.creator:
            raise PermissionDenied(MessagesException.PermissionDenied.CAN_CREATE_MORE_THAN_ONE_TOURNAMENT)
        participant.delete()
    except TournamentParticipants.DoesNotExist:
        if created_tournament and Tournaments.objects.filter(created_by=user_id).exists():
            raise PermissionDenied(MessagesException.PermissionDenied.CAN_CREATE_MORE_THAN_ONE_TOURNAMENT)

    try:
        Players.objects.get(user_id=user_id).delete()
    except Players.DoesNotExist:
        pass

    try:
        LobbyParticipants.objects.get(user_id=user_id).delete()
    except LobbyParticipants.DoesNotExist:
        pass

    try:
        request_game(endpoints.Game.fmatch_user.format(user_id=user_id), method='GET')
    except NotFound:
        return
    except APIException:
        raise ServiceUnavailable('game')

    raise Conflict(MessagesException.Conflict.ALREADY_IN_GAME)


# -------------------- BLOCK CHECK ----------------------------------------------------------------------------------- #
def are_users_blocked(request, obj, new_user):
    if obj.str_name == GameMode.tournament:
        self_user = obj.created_by
    else:
        try:
            self_user = obj.participants.get(creator=True).user_id
        except (LobbyParticipants.DoesNotExist, TournamentParticipants.DoesNotExist):
            raise NotFound(MessagesException.NotFound.CREATOR)

    try:
        request_users(endpoints.Users.fare_blocked.format(user1_id=self_user, user2_id=new_user), 'GET', request)
        return True
    except NotFound:
        return False
    except APIException:
        raise ServiceUnavailable('users')
