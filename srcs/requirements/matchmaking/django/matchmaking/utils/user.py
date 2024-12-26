from django.core.exceptions import PermissionDenied
from lib_transcendence.exceptions import Conflict, MessagesException, ServiceUnavailable
from lib_transcendence.services import request_game
from lib_transcendence import endpoints
from rest_framework.exceptions import APIException, NotFound

from lobby.models import LobbyParticipants
from play.models import Players
from tournament.models import TournamentParticipants, Tournaments


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

