import json
from typing import Literal

import requests
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, APIException


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Failed to connect to {service} service.'
    default_code = 'service_unavailable'

    def __init__(self, service):
        self.detail = ServiceUnavailable.default_detail.format(service=service)


def request_service(service: Literal['users', 'matchmaking'], enpoint: str, method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], data=None, authorization=None):
    if data is not None:
        data = json.dumps(data)

    headers = {'Content-Type': 'application/json'}
    if authorization is not None:
        headers['Authorization'] = authorization

    try:
        response = requests.request(
            method=method,
            url=f'http://{service}:8000/api/{enpoint}',
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


def requests_matchmaking(tournament_id, stage_id, winner, looser):
    data = {
        'tournament_id': tournament_id,
        'stage_id': stage_id,
        'winner': winner,
        'loser': looser,
    }

    return request_service('matchmaking', 'tournament/result-match/', 'POST', data)
