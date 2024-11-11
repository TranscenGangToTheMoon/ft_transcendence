from typing import Literal

from utils.credentials import new_user
from utils.generate_random import rnstr
from utils.request import make_request


def create_tournament(user=None, data=None, method: Literal['GET', 'POST', 'PATCH', 'DELETE'] = 'POST'):
    if data is None:
        data = {'name': 'Tournoi ' + rnstr(), 'size': 4}
    if user is None:
        user = new_user()
    return make_request(
        endpoint='play/tournament/',
        method=method,
        token=user['token'],
        data=data,
    )


def join_tournament(code, user=None, method: Literal['GET', 'POST', 'PATCH', 'DELETE'] = 'POST', data=None):
    if user is None:
        user = new_user()
    if data is None:
        data = {}
    else:
        method = 'PATCH'
    return make_request(
        endpoint=f'play/tournament/{code}/',
        method=method,
        token=user['token'],
        data=data,
    )


def search_tournament(query=None, user=None, data=None):
    if user is None:
        user = new_user()
    if data is None:
        data = {'q': query}
    return make_request(
        endpoint='play/tournament/search/',
        method='GET',
        token=user['token'],
        data=data,
    )


def kick_user(user, user_kick, code):
    return make_request(
        endpoint=f'play/tournament/{code}/kick/{user_kick["id"]}/',
        token=user['token'],
        method='DELETE',
    )
