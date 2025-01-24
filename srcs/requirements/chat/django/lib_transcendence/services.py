from typing import Literal

from lib_transcendence.request import request_service
from lib_transcendence.exceptions import MessagesException
from rest_framework.exceptions import NotAuthenticated


def request_users(endpoint: Literal['users/me/', 'validate/chat/', 'blocked/<>/'], method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], data=None, token=None):
    kwargs = {}
    if token is not None:
        kwargs['token'] = token
    if data is not None:
        kwargs['data'] = data

    return request_service('users', endpoint, method, **kwargs)


def request_matchmaking(endpoint: str, method: Literal['POST', 'PUT', 'DELETE'], data=None):
    return request_service('matchmaking', endpoint, method, data)


def request_game(endpoint: Literal['match/', 'tournaments/', 'playing/{user_id}/'], method: Literal['GET', 'PUT', 'POST'], data=None):
    return request_service('game', endpoint, method, data)


def request_chat(endpoint: str, method: Literal['GET', 'PUT', 'DELETE'], data=None, token=None):
    return request_service('chat', endpoint, method, data, token)


def request_auth(token, endpoint: Literal['update/', 'verify/', 'delete/'], method: Literal['GET', 'PUT', 'PATCH', 'DELETE'], data=None):
    if token is None:
        raise NotAuthenticated(MessagesException.Authentication.NOT_AUTHENTICATED)

    return request_service('auth', endpoint, method, data, token)




