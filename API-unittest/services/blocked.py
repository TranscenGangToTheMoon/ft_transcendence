from typing import Literal

from utils.credentials import new_user
from utils.request import make_request


def blocked_user(user, user_id=None, data=None, method: Literal['GET', 'POST'] = 'POST'):
    if data is None:
        if method == 'POST':
            if user_id is None:
                user_id = new_user()['id']
            data = {'user_id': user_id}
        else:
            data = {}

    return make_request(
        endpoint='users/me/blocked/',
        method=method,
        data=data,
        token=user['token'],
    )


def unblocked_user(user, block_id):
    return make_request(
        endpoint=f'users/me/blocked/{block_id}/',
        method='DELETE',
        token=user['token'],
    )


def are_blocked(user1_id, user2_id):
    return make_request(
        endpoint=f'private/users/blocked/{user1_id}/{user2_id}/',
        port=8005,
    )
