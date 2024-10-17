import json
from getpass import getpass

import requests

base_enpoint = 'http://localhost:8000/api/auth/'


def ipt_username():
    return input('enter username -> ')


def auth_guest():
    r = requests.post(base_enpoint + 'guest/')
    print(r.status_code, r.json())
    return r.json()


def register_guest():
    access_token = auth_guest()['access']
    r = requests.post(
        base_enpoint + 'guest/register/',
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token},
        data=json.dumps({'username': ipt_username(), 'password': getpass()})
    )
    print(r.status_code, r.json())
    return r.json()


def register():
    r = requests.post(
        base_enpoint + 'register/',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({'username': ipt_username(), 'password': getpass()})
    )
    print(r.status_code, r.json())
    return r.json()


def get_token():
    r = requests.post(
        base_enpoint + 'token/',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({'username': ipt_username(), 'password': getpass()})
    )
    print(r.status_code, r.json())
    return r.json()


def verify_token(token=None):
    if token is None:
        token = get_token()
    r = requests.get(
        base_enpoint + 'token/verify/',
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token['access']}
    )
    print(r.status_code, r.json())
    return r.json()


print(register())
