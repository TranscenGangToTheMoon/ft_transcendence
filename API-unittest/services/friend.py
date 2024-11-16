from typing import Literal

from utils.credentials import new_user
from utils.request import make_request


def send_friend_request(sender=None, receiver=None, method: Literal['POST', 'GET'] = 'POST', data=None):
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


def receive_friend_requests(user):
    return make_request(
        endpoint='users/me/friend_requests/receive/',
        token=user['token'],
    )


def accept_friend_request(receiver=None, sender=None, method: Literal['POST', 'GET', 'DELETE'] = 'POST', data=None):
    if receiver is None:
        receiver = new_user()
    if method == 'POST':
        if sender is None:
            sender = new_user()
        if data is None:
            data = {'username': sender['username']}# todo remake this ?
    elif data is None:
        data = {}
    return make_request(
        endpoint='users/me/friends/',
        method=method,
        token=receiver['token'],
        data=data,
    )


def create_friend(user1=None, user2=None):
    if user1 is None:
        user1 = new_user()
    if user2 is None:
        user2 = new_user()
    response_request = send_friend_request(user1, user2)
    response_accept = accept_friend_request(user2, user1)
    return [response_request, response_accept]
