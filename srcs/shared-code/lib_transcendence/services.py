from typing import Literal

from rest_framework.exceptions import NotAuthenticated

from lib_transcendence import endpoints
from lib_transcendence.request import request_service


def request_users(endpoint: Literal['users/me/', 'validate/chat/', 'blocked/<>/'], method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], request=None, data=None):
    kwargs = {}
    if request is not None:
        kwargs['token'] = request.headers.get('Authorization')
        if kwargs['token'] is None:
            raise NotAuthenticated()
    if data is not None:
        kwargs['data'] = data

    return request_service('users', endpoint, method, **kwargs)


def request_matchmaking(endpoint: str, method: Literal['POST', 'DELETE'], data=None):
    return request_service('matchmaking', endpoint, method, data)


def request_tournament_matchmaking(tournament_id, stage_id, winner, looser):
    data = {
        'tournament_id': tournament_id,
        'stage_id': stage_id,
        'winner': winner,
        'loser': looser,
    }

    return request_matchmaking('tournament/result-match/', 'POST', data)


def request_game(endpoint: Literal['match/', 'tournaments/', 'playing/{user_id}/'], method: Literal['GET', 'POST'] = 'POST', data=None):
    return request_service('game', endpoint, method, data)


def request_chat(endpoint: str, method: Literal['PATCH', 'DELETE'] = 'PATCH', data=None):
    return request_service('chat', endpoint, method, data)


def request_auth(token, endpoint: Literal['update/', 'verify/', 'delete/'], method: Literal['GET', 'PUT', 'PATCH', 'DELETE'], data=None):
    if token is None:
        raise NotAuthenticated()

    return request_service('auth', endpoint, method, data, token)


def post_messages(chat_id: int, content: str, token: str):
    return request_service('chat', endpoints.Chat.fmessage.format(chat_id=chat_id), 'POST', {'content': content}, token)
