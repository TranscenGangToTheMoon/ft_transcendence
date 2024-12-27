from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied
from lib_transcendence.exceptions import MessagesException, ResourceExists

from baning.utils import is_baned
from blocking.utils import are_users_blocked
from lobby.models import Lobby, LobbyParticipants
from matchmaking.utils.user import verify_user
from tournament.models import Tournament, TournamentParticipants


def get_place(model, create, **kwargs):
    name = model.__name__
    allowed_keys = ('id', 'code')

    key = list(kwargs)[0]
    assert len(kwargs) == 1 and key in allowed_keys

    value = kwargs[key]
    if value is None:
        raise serializers.ValidationError({key: [MessagesException.ValidationError.REQUIRED.format(obj=f'{name} {key}')]})
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        if create:
            raise NotFound(MessagesException.NotFound.NOT_FOUND.format(obj=name))
        raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG.format(obj=name.lower()))


def get_lobby(code, create=False):
    return get_place(Lobby, create, code=code)


def get_tournament(create=False, **kwargs):
    return get_place(Tournament, create, **kwargs)


def verify_place(user, model):
    name = type(model).__name__

    def get_place_creator():
        if isinstance(model, Tournament):
            return model.created_by
        else:
            try:
                return model.participants.get(creator=True).user_id
            except (LobbyParticipants.DoesNotExist, TournamentParticipants.DoesNotExist):
                raise NotFound(MessagesException.NotFound.CREATOR)

    if model.participants.filter(user_id=user['id']).exists():
        raise ResourceExists(MessagesException.ResourceExists.JOIN.format(obj=name.lower()))

    if is_baned(model.code, user['id']) or are_users_blocked(user['id'], get_place_creator()):
        raise NotFound(MessagesException.NotFound.NOT_FOUND.format(obj=name.title()))

    if isinstance(model, Tournament) and model.is_started:
        raise PermissionDenied(MessagesException.PermissionDenied.TOURNAMENT_ALREADY_STARTED)

    verify_user(user['id'])

    if model.is_full:
        raise PermissionDenied(MessagesException.PermissionDenied.IS_FULL.format(obj=name.title()))

