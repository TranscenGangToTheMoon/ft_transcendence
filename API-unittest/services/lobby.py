from typing import Literal

from utils.request import make_request


def create_lobby(user, data=None, method: Literal['GET', 'POST', 'PATCH', 'DELETE'] = 'POST'):
    if data is None:
        data = {'game_mode': 'clash'}
    return make_request(
        endpoint='play/lobby/',
        method=method,
        token=user['token'],
        data=data,
    )


def join_lobby(user, code, method: Literal['GET', 'POST', 'PATCH', 'DELETE'] = 'POST', data=None):
    if data is None:
        data = {}
    else:
        method = 'PATCH'
    return make_request(
        endpoint=f'play/lobby/{code}/',
        method=method,
        token=user['token'],
        data=data,
    )


def kick_user(user, user_kick, code):
    return make_request(
        endpoint=f'play/lobby/{code}/kick/{user_kick["id"]}/',
        token=user['token'],
        method='DELETE',
    )
