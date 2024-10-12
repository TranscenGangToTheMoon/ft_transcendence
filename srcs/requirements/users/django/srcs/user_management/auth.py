import json
from typing import Literal

import requests
from rest_framework.exceptions import AuthenticationFailed


def requests_auth(token, enpoint: Literal['update/', 'verify/', 'delete/'], method: Literal['GET', 'PUT', 'PATCH', 'DELETE'], data=None):
    if token is None:
        raise AuthenticationFailed('Authentication credentials were not provided.')

    try:
        response = requests.request(
            method=method,
            url='http://auth:8000/api/auth/' + enpoint,
            headers={
                'Authorization': token,
                'Content-Type': 'application/json'
            },
            data=data
        )
        if response.status_code == 204:
            return
        json_data = response.json()
        if response.status_code not in (200, 201, 202, 203, 205, 206):
            raise AuthenticationFailed(json_data)
    except (requests.ConnectionError, requests.exceptions.JSONDecodeError):
        raise AuthenticationFailed('Failed to connect to auth service')
    return json_data


def auth_verify(token):
    return requests_auth(token, 'verify/', method='GET')


def auth_update(token, data):
    return requests_auth(token, 'update/', method='PUT', data=json.dumps(data))


def auth_delete(token, data):
    requests_auth(token, 'delete/', method='DELETE', data=json.dumps(data))
