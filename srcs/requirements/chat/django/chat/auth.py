import json
from typing import Literal

import requests
from rest_framework import permissions, serializers
from rest_framework.exceptions import AuthenticationFailed


def requests_users(request, enpoint: Literal['me/', 'validate/chat/'], method: Literal['GET', 'PUT', 'PATCH', 'DELETE'], data=None):
    if request is None:
        raise serializers.ValidationError({'detail': 'Request is required.'})
    token = request.headers.get('Authorization')
    if token is None:
        raise AuthenticationFailed('Authentication credentials were not provided.')

    if data is not None:
        data = json.dumps(data)

    try:
        response = requests.request(
            method=method,
            url='http://users:8000/api/users/' + enpoint,
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
        raise AuthenticationFailed('Failed to connect to users service')
    return json_data


class IsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        json_data = requests_users(request, 'me/', 'GET')
        request.data['auth_user'] = json_data
        request.user.id = json_data['id']
        request.user.username = json_data['username']
        return True


def get_auth_user(request=None):
    if request is None:
        raise serializers.ValidationError({'detail': 'Request is required.'})
    return request.data['auth_user']
