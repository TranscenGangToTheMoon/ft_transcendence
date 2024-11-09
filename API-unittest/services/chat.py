from typing import Literal

from utils.request import make_request


def accept_chat(user, accept_chat_from: Literal['everyone', 'friend_only', 'none'] = 'everyone'):
    return make_request(
        endpoint='users/me/',
        method='PATCH',
        token=user['token'],
        data={'accept_chat_from': accept_chat_from}
    )


def create_chat(user1, username=None, data=None, method: Literal['GET', 'POST'] = 'POST'):
    if data is None and method == 'POST':
        data = {'username': username, 'type': 'private_message'}
    return make_request(
        endpoint='chat/',
        method=method,
        token=user1['token'],
        data=data,
    )
