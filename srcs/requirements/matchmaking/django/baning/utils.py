from django.core.exceptions import PermissionDenied
from lib_transcendence.sse_events import EventCode, create_sse_event
from lib_transcendence.exceptions import MessagesException
from rest_framework.exceptions import NotFound

from baning.models import Banned
from lobby.models import LobbyParticipants
from tournament.models import TournamentParticipants


def is_banned(code: str, user_id: int) -> bool:
    try:
        Banned.objects.get(code=code, banned_user_id=user_id)
        return True
    except Banned.DoesNotExist:
        return False


def banned(banned_participants: LobbyParticipants | TournamentParticipants, create_ban: bool = True):
    if create_ban:
        Banned.objects.create(code=banned_participants.place.code, banned_user_id=banned_participants.user_id)
    if isinstance(banned_participants, LobbyParticipants):
        ban_code = EventCode.LOBBY_BANNED
    else:
        ban_code = EventCode.TOURNAMENT_BANNED
    create_sse_event(banned_participants.user_id, ban_code)


def ban_yourself(user_id, ban_user_id):
    if user_id == ban_user_id:
        raise PermissionDenied(MessagesException.PermissionDenied.BAN_YOURSELF)


def get_participants_for_baning(model, user_id):
    try:
        return model.participants.get(user_id=user_id)
    except (LobbyParticipants.DoesNotExist, TournamentParticipants.DoesNotExist):
        raise NotFound(MessagesException.PermissionDenied.USER_NOT_BELONG.format(obj=type(model).__name__.lower()))
