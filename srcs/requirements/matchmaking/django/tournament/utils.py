from datetime import datetime, timezone

from lib_transcendence import endpoints
from lib_transcendence.services import request_game, request_users
from lib_transcendence.sse_events import create_sse_event, EventCode

from tournament.serializers import TournamentSerializer, TournamentStageSerializer


def finish_tournament(tournament, winner_user_id):
    data = TournamentSerializer(tournament).data
    data['finish_at'] = datetime.now(timezone.utc)
    data['stages'] = TournamentStageSerializer(tournament.stages.all(), many=True).data
    request_game(endpoints.Game.tournaments, method='POST', data=data)
    create_sse_event(tournament.users_id(), EventCode.TOURNAMENT_FINISH, {'id': tournament.id}, {'name': tournament.name, 'username': winner_user_id})
    request_users(endpoints.Users.result_tournament, method='POST', data={'winner': winner_user_id})
    tournament.delete()
