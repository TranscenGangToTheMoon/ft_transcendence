import json
from getpass import getpass

import requests

base_enpoint = 'http://localhost:8000/api/auth/'


def ipt_username():
    return input('enter username -> ')


def auth_guest():
    r = requests.post(base_enpoint + 'guest/')
    print(r.status_code)
    print(r.json())
    return r.json()


def register():
    access_token = auth_guest()['access']
    r = requests.put(
        base_enpoint + 'register/',
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token},
        data=json.dumps({'username': ipt_username(), 'password': getpass()})
    )
    print(r.status_code)
    print(r.json())
    return r.json()


def login():
    r = requests.post(
        base_enpoint + 'login/',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({'username': ipt_username(), 'password': getpass()})
    )
    print(r.status_code)
    print(r.json())
    return r.json()


def verify_token(token=None):
    if token is None:
        token = login()
    r = requests.get(
        base_enpoint + 'verify/',
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token['access']}
    )
    print(r.status_code)
    print(r.json())
    return r.json()
