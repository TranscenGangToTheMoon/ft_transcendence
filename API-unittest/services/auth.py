from typing import Literal

from utils.generate_random import rnstr
from utils.request import make_request


def register(username=None, password=None, data=None, method='POST'):
    if data is None:
        data = {}

    if username is not None:
        data['username'] = username
    else:
        data['username'] = 'register_test' + rnstr(10)

    if password is not None:
        data['password'] = password
    else:
        data['password'] = 'register_' + rnstr(15)

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
            data['password'] = 'password_guest' + rnstr(10)

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
