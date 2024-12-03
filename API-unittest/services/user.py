from typing import Literal

from utils.credentials import new_user
from utils.request import make_request


def get_user(user=None, user2_id=None):
    if user is None:
        user = new_user()
    if user2_id is None:
        user2_id = new_user()['id']

    return make_request(
        endpoint=f'users/{user2_id}/',
        token=user['token'],
    )


def me(user, method: Literal['GET', 'DELETE', 'PATCH'] = 'GET', data=None, password=False):
    if method in ('PATCH', 'DELETE') and password:
        data = {'password': user['password']}
    elif data is None:
        data = {}
    return make_request(
        endpoint=f'users/me/',
        token=user['token'],
        method=method,
        data=data,
    )
