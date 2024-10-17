import json
from typing import Literal

import requests
from rest_framework import permissions, serializers
from rest_framework.exceptions import AuthenticationFailed

from block.models import Block
from users.models import Users


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
    return requests_auth(token, 'update/', method='PATCH', data=json.dumps(data))


def auth_delete(token, data):
    requests_auth(token, 'delete/', method='DELETE', data=json.dumps(data))


class IsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):

        json_data = auth_verify(request.headers.get('Authorization'))

        try:
            user = Users.objects.get(id=json_data['id'])
            if user.is_guest != json_data['is_guest']:
                user.is_guest = json_data['is_guest']
                user.save()
            if user.username != json_data['username']:
                user.username = json_data['username']
                user.save()
        except Users.DoesNotExist:
            user = Users.objects.create(**json_data)
        request.user.id = user.id
        request.user.username = user.username
        return True


def get_user(request=None, id=None):
    if id is None:
        if request is None:
            raise serializers.ValidationError({'detail': 'Request is required.'})
        id = request.user.id
    return Users.objects.get(pk=id)


def validate_username(username, user):
    try:
        assert username is not None
        valide_username = Users.objects.get(username=username)
        assert valide_username.is_guest is False
        assert not Block.objects.filter(user=valide_username, blocked=user).exists()
    except (Users.DoesNotExist, AssertionError):
        raise serializers.ValidationError({'username': ['This user does not exist.']})
    return valide_username
