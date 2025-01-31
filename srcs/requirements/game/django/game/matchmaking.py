from rest_framework.exceptions import APIException

from lib_transcendence import endpoints
from lib_transcendence.game import GameMode
from lib_transcendence.services import request_matchmaking


def send_finish_match_matchmaking(data):
    try:
        if isinstance(data, int):
            kwargs = {'game_mode': GameMode.TOURNAMENT, 'tournament_id': data}
        else:
            kwargs = {'game_mode': data.game_mode, 'players': data.users_id()}
        request_matchmaking(endpoints.Matchmaking.finish_match, 'POST', kwargs)
    except APIException:
        pass
