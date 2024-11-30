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


def get_me(user):
    return make_request(
        endpoint=f'users/me/',
        token=user['token'],
    )
