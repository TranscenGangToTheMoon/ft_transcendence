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


def request_chat_id(user1, chat_id, data=None, method: Literal['GET', 'DELETE'] = 'GET'):
    if data is None:
        data = {}
    return make_request(
        endpoint=f'chat/{chat_id}/',
        method=method,
        token=user1['token'],
        data=data,
    )


def create_message(user, chat_id, message=None, data=None, method: Literal['GET', 'POST'] = 'POST'):
    if data is None and method == 'POST':
        data = {'content': message}

    kwargs = {'endpoint': f'{chat_id}/messages/', 'method': method, 'token': user['token'], 'data': data, 'port': 8002}
    if method == 'GET':
        kwargs.pop('data')
        kwargs.pop('port')
        kwargs['endpoint'] = 'chat/' + kwargs['endpoint']

    return make_request(**kwargs)
