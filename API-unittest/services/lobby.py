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


def ban_user(user, user_ban, code):
    return make_request(
        endpoint=f'play/lobby/{code}/ban/{user_ban["id"]}/',
        token=user['token'],
        method='DELETE',
    )


def invite_user(user, user_invite, code, service: Literal['lobby', 'tournament'] = 'lobby'):
    return make_request(
        endpoint=f'play/{service}/{code}/invite/{user_invite["id"]}/',
        token=user['token'],
        method='POST',
    )
