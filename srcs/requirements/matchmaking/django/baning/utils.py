from django.core.exceptions import PermissionDenied
from lib_transcendence.services import create_sse_event
from lib_transcendence.sse_events import EventCode
from lib_transcendence.exceptions import MessagesException

from baning.models import Baned
from lobby.models import LobbyParticipants
from tournament.models import TournamentParticipants


def is_baned(code: str, user_id: int) -> bool:
    try:
        Baned.objects.get(code=code, baned_user_id=user_id)
        return True
    except Baned.DoesNotExist:
        return False


def baned(participant: LobbyParticipants | TournamentParticipants):
    Baned.objects.create(code=participant.place.code, baned_user_id=participant.user_id)
    if isinstance(participant, LobbyParticipants):
        ban_code = EventCode.LOBBY_BAN
    else:
        ban_code = EventCode.TOURNAMENT_BAN
    create_sse_event(participant.user_id, ban_code, kwargs={'username': participant.user_id})


def ban_yourself(user_id, ban_user_id):
    if user_id == ban_user_id:
        raise PermissionDenied(MessagesException.PermissionDenied.BAN_YOURSELF)


def get_participants_for_baning(model, user_id):
    try:
        return model.participants.get(user_id=user_id)
    except (LobbyParticipants.DoesNotExist, TournamentParticipants.DoesNotExist):
        raise PermissionDenied(MessagesException.PermissionDenied.USER_NOT_BELONG.format(obj=type(model).__name__.lower()))
