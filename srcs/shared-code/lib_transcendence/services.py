from typing import Literal

from rest_framework.exceptions import NotAuthenticated
from lib_transcendence.request import request_service


def requests_users(endpoint: Literal['users/me/', 'validate/chat/', 'blocked/<>/'], method: Literal['GET', 'PUT', 'PATCH', 'DELETE'], request=None):
    kwargs = {}
    if request is not None:
        kwargs['authorization'] = request.headers.get('Authorization')
        if kwargs['authorization'] is None:
            raise NotAuthenticated()

    return request_service('users', endpoint, method, **kwargs)


def requests_matchmaking(endpoint: str, method: Literal['POST', 'DELETE'], data=None):
    return request_service('matchmaking', endpoint, method, data)


def requests_tournament_matchmaking(tournament_id, stage_id, winner, looser):
    data = {
        'tournament_id': tournament_id,
        'stage_id': stage_id,
        'winner': winner,
        'loser': looser,
    }

    return requests_matchmaking('tournament/result-match/', 'POST', data)


def requests_game(endpoint: Literal['match/', 'tournaments/', 'playing/{user_id}/'], method: Literal['GET', 'POST'] = 'POST', data=None):
    return request_service('game', endpoint, method, data)


def requests_chat(endpoint: str, method: Literal['PATCH', 'DELETE'] = 'PATCH', data=None):
    return request_service('chat', endpoint, method, data)
