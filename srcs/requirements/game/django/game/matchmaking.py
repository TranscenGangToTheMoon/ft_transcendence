from rest_framework.exceptions import APIException

from lib_transcendence import endpoints
from lib_transcendence.game import GameMode
from lib_transcendence.services import request_matchmaking


def send_finish_match_matchmaking(match=None, tournament=None):
    try:
        if match:
            kwargs = {'game_mode': match.game_mode, 'players': match.users_id()}
        else:
            kwargs = {'game_mode': GameMode.TOURNAMENT, 'tournament_id': tournament.id}
        request_matchmaking(endpoints.Matchmaking.finish_match, 'POST', kwargs)
    except APIException:
        pass
