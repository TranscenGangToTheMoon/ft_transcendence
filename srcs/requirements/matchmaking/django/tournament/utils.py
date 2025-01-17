import time
from datetime import datetime, timezone

from lib_transcendence import endpoints
from lib_transcendence.services import request_game, request_users
from lib_transcendence.sse_events import create_sse_event, EventCode
from rest_framework.exceptions import APIException

from tournament.models import Tournament
from tournament.serializers import TournamentSerializer, TournamentStageSerializer


def finish_tournament(tournament_id, winner_user_id):
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return
    data = TournamentSerializer(tournament).data
    data['finish_at'] = datetime.now(timezone.utc)
    data['stages'] = TournamentStageSerializer(tournament.stages.all(), many=True).data
    request_game(endpoints.Game.tournaments, method='POST', data=data)
    create_sse_event(tournament.users_id(), EventCode.TOURNAMENT_FINISH, {'id': tournament.id}, {'name': tournament.name, 'username': winner_user_id})
    request_users(endpoints.Users.result_tournament, method='POST', data={'winner': winner_user_id})
    tournament.delete()


def create_match_new_stage(tournament_id, current_stage, winner):
    time.sleep(3)

    try:
        tournament = Tournament.objects.get(id=tournament_id) # todo remake
    except Tournament.DoesNotExist:
        return
    if current_stage.matches.filter(finished=False).exists(): # todo remake
        return
    participants = tournament.participants.filter(still_in=True).order_by('index')
    ct = participants.count()

    try:
        for i in range(0, ct, 2):
            match = tournament.matches.create(n=tournament.get_nb_matches(), stage=winner.stage, user_1=participants[i], user_2=participants[i + 1])
            match.post()
    except APIException:
        tournament.delete() # todo test
