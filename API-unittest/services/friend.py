from typing import Literal

from utils.credentials import new_user
from utils.request import make_request


def friend_requests(sender=None, receiver=None, method: Literal['POST', 'GET'] = 'POST', data=None):
    if sender is None:
        sender = new_user()
    if method == 'POST':
        if receiver is None:
            receiver = new_user()
        if data is None:
            data = {'username': receiver['username']}
    else:
        data = {}
    return make_request(
        endpoint='users/me/friend_requests/',
        method=method,
        token=sender['token'],
        data=data,
    )


def get_friend_requests_received(user):
    return make_request(
        endpoint='users/me/friend_requests/received/',
        token=user['token'],
    )


    return make_request(
        endpoint='users/me/friends/',

def friend(user, friendship_id, method: Literal['GET', 'DELETE'] = 'GET'):
    return make_request(
        endpoint=f'users/me/friends/{friendship_id}/',
        method=method,
        token=user['token'],
    )


def friend_request(friend_request_id, user=None, method: Literal['POST', 'GET', 'DELETE'] = 'POST'):
    if user is None:
        user = new_user()

    return make_request(
        endpoint=f'users/me/friend_requests/{friend_request_id}/',
        method=method,
        token=user['token'],
    )


def create_friendship(user1=None, user2=None):
    if user1 is None:
        user1 = new_user()
    if user2 is None:
        user2 = new_user()
    response_request = friend_requests(user1, user2)
    response_accept = friend_request(response_request.json['id'], user2)
    return [response_request, response_accept]
