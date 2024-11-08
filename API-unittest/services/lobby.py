from typing import Literal

from utils.credentials import new_user
from utils.request import make_request


def create_lobby(user=None, data=None, method: Literal['GET', 'POST', 'PATCH', 'DELETE'] = 'POST'):
    if data is None:
        data = {'game_mode': 'clash'}
    if user is None:
        user = new_user()
    return make_request(
        endpoint='play/lobby/',
        method=method,
        token=user['token'],
        data=data,
    )


def join_lobby(code, user=None, method: Literal['GET', 'POST', 'PATCH', 'DELETE'] = 'POST', data=None):
    if user is None:
        user = new_user()
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
