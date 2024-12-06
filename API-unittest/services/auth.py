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


    kwargs = {
        'endpoint': 'auth/register/',
        'method': method,
        'data': data
    }

    if guest is not None and method == 'PATCH':
        kwargs['token'] = guest['token']
        kwargs['data'] = {'username': guest['username'], 'password': 'password_' + guest['username']}

    return make_request(**kwargs)
