from django.core.exceptions import PermissionDenied
from lib_transcendence.exceptions import Conflict, MessagesException
from lib_transcendence.game import GameMode
from lib_transcendence.services import request_game
from lib_transcendence import endpoints
from rest_framework.exceptions import APIException

from lobby.models import LobbyParticipants
from play.models import Players
from tournament.models import TournamentParticipants, Tournament


def verify_user(user_id, created_tournament=False, join_tournament_id=None, from_place=False):
    try:
        place = request_game(endpoints.Game.fuser.format(user_id=user_id), method='GET')
    except APIException:
        try:
            participant = TournamentParticipants.objects.get(user_id=user_id)
            if created_tournament and participant.creator:
                raise PermissionDenied(MessagesException.PermissionDenied.CAN_CREATE_MORE_THAN_ONE_TOURNAMENT)
            if from_place:
                return participant
            else:
                participant.delete()
        except TournamentParticipants.DoesNotExist:
            if created_tournament and Tournament.objects.filter(created_by=user_id).exists():
                raise PermissionDenied(MessagesException.PermissionDenied.CAN_CREATE_MORE_THAN_ONE_TOURNAMENT)

        try:
            player = Players.objects.get(user_id=user_id)
            if from_place:
                return player
            else:
                player.delete()
        except Players.DoesNotExist:
            pass

        try:
            player = LobbyParticipants.objects.get(user_id=user_id)
            if from_place:
                return player
            else:
                player.delete()
        except LobbyParticipants.DoesNotExist:
            pass

        return

    if join_tournament_id and place['type'] == GameMode.TOURNAMENT and place['id'] == join_tournament_id:
        return 'reconnect'

    raise Conflict(MessagesException.Conflict.ALREADY_IN_GAME_OR_TOURNAMENT)
