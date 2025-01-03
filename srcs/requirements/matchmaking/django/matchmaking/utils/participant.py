from rest_framework.exceptions import NotFound, PermissionDenied
from lib_transcendence.users import retrieve_users
from lib_transcendence.exceptions import MessagesException

from lobby.models import LobbyParticipants, Lobby
from tournament.models import TournamentParticipants


def get_participants(obj, add_fields: list[str] = None):
    fields = ['user_id', 'creator', 'join_at']
    if add_fields is not None:
        fields.extend(add_fields)
    participants = {p['user_id']: p for p in obj.participants.all().values(*fields)}
    results = retrieve_users(list(participants))
    for participant in results:
        for f in fields[1:]:
            participant[f] = participants[participant['id']][f]
    return results


def get_participant(model, obj, user_id, creator_check=False, from_place=False):
    if model is TournamentParticipants:
        name = 'tournament'
    else:
        name = 'lobby'

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
    return get_participant(LobbyParticipants, lobby, user_id, creator_check, from_place)


def get_tournament_participant(tournament, user_id, creator_check=False, from_place=False):
    return get_participant(TournamentParticipants, tournament, user_id, creator_check, from_place)


# todo add event for delete friend, and delete friend request
