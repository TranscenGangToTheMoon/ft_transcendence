from typing import Literal

from utils.request import make_request
from utils.generate_random import rnstr


# -------------------- SERVICES -------------------------------------------------------------------------------------- #
TESTS = [
    'test_auth',
    'test_blocked',
    'test_chat',
    'test_friends',
    'test_game',
    'test_lobby',
    'test_matchmaking',
    'test_play',
    'test_sse',
    'test_tournament',
    'test_users',
]


# -------------------- REQUEST --------------------------------------------------------------------------------------- #
def auth_guest():
    return make_request('auth/guest/', 'POST')


def register(data):
    return make_request('auth/register/', 'POST', data=data)


def login(username=None, password=None, data=None):
    if data is None:
        data = {'username': username, 'password': password}
    return make_request('auth/login/', 'POST', data=data)


# -------------------- GET TOKEN ------------------------------------------------------------------------------------- #
def get_token(type: Literal['login', 'register', 'guest'], username=None, password=None):
    if type == 'guest':
        token = auth_guest().json
    else:
        if username is None:
            username = ''.join(rnstr(20))
        if password is None:
            password = ''.join(rnstr(20))
        data = {'username': username, 'password': password}

        if type == 'login':
            token = login(data=data).json
        else:
            token = register(data).json
    return token


# -------------------- GET USER -------------------------------------------------------------------------------------- #
def get_service():
    import inspect

    origin_file = inspect.currentframe()
    while True:
        service_name = origin_file.f_code.co_filename.split('/')[-1].split('.')[0]
        if origin_file.f_back is None or service_name in TESTS:
            break
        origin_file = origin_file.f_back

    return service_name.replace('test_', '')


def new_user(username=None, password=None, get_me=False):
    if username is None:
        username = f'{get_service()}-user-' + rnstr()
    if password is None:
        password = 'password-' + rnstr(15)
    _new_user = {'username': username, 'password': password}
    token = get_token('register', _new_user['username'], password)
    _new_user['token'] = token['access']
    _new_user['refresh'] = token['refresh']
    if get_me:
        response = make_request(
            endpoint='users/me/',
            token=_new_user['token'],
        )
        assert response.status_code == 200
        _new_user['id'] = response.json['id']
    return _new_user


def guest_user():
    _new_user = {}
    token = get_token('guest')
    _new_user['token'] = token['access']
    _new_user['refresh'] = token['refresh']
    response = make_request(
        endpoint='users/me/',
        token=_new_user['token'],
    )
    assert response.status_code == 200
    _new_user['id'] = response.json['id']
    _new_user['username'] = response.json['username']
    return _new_user
