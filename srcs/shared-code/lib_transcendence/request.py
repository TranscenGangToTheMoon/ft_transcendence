import json
from typing import Literal

from rest_framework import status
from rest_framework.exceptions import APIException, AuthenticationFailed, PermissionDenied, MethodNotAllowed, NotFound
import requests


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Failed to connect to {service} service.'
    default_code = 'service_unavailable'

    def __init__(self, service):
        self.detail = ServiceUnavailable.default_detail.format(service=service)


def request_service(service: Literal['auth', 'chat', 'game', 'matchmaking', 'users'], endpoint: str, method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], data=None, authorization=None):
    if data is not None:
        data = json.dumps(data)

    headers = {'Content-Type': 'application/json'}
    if authorization is not None:
        headers['Authorization'] = authorization

    try:
        print(method, f'[{service}] => /api/{endpoint}', flush=True)
        response = requests.request(
            method=method,
            url=f'http://{service}:8000/api/{endpoint}',
            headers=headers,
            data=data
        )

        if response.status_code == 204:
            return

        json_data = response.json()
        print('JSON =', json_data, flush=True)
        if response.status_code == 400:
            raise PermissionDenied(json_data)
        if response.status_code == 401:
            raise AuthenticationFailed(json_data)
        if response.status_code == 403:
            raise PermissionDenied(json_data)
        if response.status_code == 404:
            raise NotFound(json_data)
        if response.status_code == 405:
            raise MethodNotAllowed(method)
        if response.status_code == 503:
            raise ServiceUnavailable(service)
    except (requests.ConnectionError, requests.exceptions.JSONDecodeError):
        raise ServiceUnavailable(service)
    return json_data
