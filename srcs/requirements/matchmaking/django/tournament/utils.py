import time
from datetime import datetime, timezone

from lib_transcendence import endpoints
from lib_transcendence.services import request_game, request_users
from lib_transcendence.sse_events import create_sse_event, EventCode
from rest_framework.exceptions import APIException

from tournament.serializers import TournamentSerializer, TournamentStageSerializer


def finish_tournament(tournament_id, winner_user_id):
    from tournament.models import Tournament

    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return
    tournament.finish()
    data = TournamentSerializer(tournament).data
    data['finish_at'] = datetime.now(timezone.utc)
    data['stages'] = TournamentStageSerializer(tournament.stages.all(), many=True).data
    request_game(endpoints.Game.tournaments, method='POST', data=data)
    create_sse_event(tournament.users_id(), EventCode.TOURNAMENT_FINISH, {'id': tournament.id}, {'name': tournament.name, 'username': winner_user_id})
    request_users(endpoints.Users.result_tournament, method='POST', data={'winner': winner_user_id})
    tournament.delete()


def create_match_new_stage(tournament_id):
    from tournament.models import Tournament

    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return
    matches = tournament.current_stage.matches.all()
    if tournament.update_stage or matches.filter(finished=False).exists():
        return

    tournament.set_update_stage(True)
    time.sleep(3)
    stage = tournament.stages.get(stage=tournament.current_stage.stage - 1)

    spectate = {}
    try:
        previous = None
        for match in matches.order_by('n'):
            if previous is None:
                previous = match
                continue
            match = tournament.matches.create(n=tournament.get_nb_matches(), stage=stage, user_1=previous.winner, user_2=match.winner)
            match.post()
            spectate[match.id] = match.match_code
            previous = None
    except APIException:
        tournament.delete()

    tournament.current_stage = stage
    create_sse_event(tournament.users_id({'still_in': False}), EventCode.TOURNAMENT_AVAILABLE_SPECTATE_MATCHES, spectate)
    tournament.set_update_stage(False)
