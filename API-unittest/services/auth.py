from typing import Literal

from utils.request import make_request


def register(username=None, password=None, data=None, method='POST'):
    if data is None and password is not None and username is not None:
        data = {'username': username, 'password': password}

    return make_request(
        endpoint='auth/register/',
        method=method,
        data=data
    )


def register_guest(guest=None, username=None, password=None, data=None, method='PATCH', token=None):
    if data is None:
        data = {}

        if username is not None:
            data['username'] = username
        elif guest is not None:
            data['username'] = guest['username']

        if password is not None:
            data['password'] = password
        elif guest is not None:
            data['password'] = 'password_' + guest['username']

    kwargs = {
        'endpoint': 'auth/register/guest/',
        'method': method,
        'data': data,
    }
    if token is None:
        if guest is not None:
            kwargs['token'] = guest['token']
    else:
        kwargs['token'] = token

    return make_request(**kwargs)
