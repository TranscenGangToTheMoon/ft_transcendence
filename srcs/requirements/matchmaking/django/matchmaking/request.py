import json
from typing import Literal

import requests
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed, APIException


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Failed to connect to {service} service.'
    default_code = 'service_unavailable'

    def __init__(self, service):
        self.detail = self.default_detail.format(service=service)


def request_service(service: Literal['users', 'game'], enpoint: str, method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], data=None, authorization=None):
    if data is not None:
        data = json.dumps(data, default=str)

    headers = {'Content-Type': 'application/json'}
    if authorization is not None:
        headers['Authorization'] = authorization

    try:
        response = requests.request(
            method=method,
            url=f'http://{service}:8000/api/{service}/{enpoint}',
            headers=headers,
            data=data
        )

        if response.status_code == 204:
            return

        json_data = response.json()
        if response.status_code not in (200, 201, 202, 203, 205, 206):
            raise AuthenticationFailed(json_data)
    except (requests.ConnectionError, requests.exceptions.JSONDecodeError):
        raise ServiceUnavailable(service)
    return json_data


def requests_users(request, enpoint: Literal['me/', 'validate/game/'], method: Literal['GET', 'PUT', 'PATCH', 'DELETE'], data=None):
    if request is None:
        raise serializers.ValidationError({'detail': 'Request is required.'})
    token = request.headers.get('Authorization')
    if token is None:
        raise AuthenticationFailed('Authentication credentials were not provided.')

    return request_service('users', enpoint, method, data, token)


def requests_game(enpoint: Literal['match/', 'tournament/'], data):
    return request_service('game', enpoint, 'POST', data)
