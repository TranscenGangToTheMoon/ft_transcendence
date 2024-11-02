import json
from typing import Literal

import requests
from lib_transcendence.request import request_service
from rest_framework import permissions, serializers
from rest_framework.exceptions import AuthenticationFailed

from users.models import Users


def requests_auth(token, endpoint: Literal['update/', 'verify/', 'delete/'], method: Literal['GET', 'PUT', 'PATCH', 'DELETE'], data=None):
    if token is None:
        raise AuthenticationFailed('Authentication credentials were not provided.')

    return request_service('auth', 'auth/' + endpoint, method, data, token)


def auth_verify(token):
    return requests_auth(token, 'verify/', method='GET')


def auth_update(token, data):
    return requests_auth(token, 'update/', method='PATCH', data=data)


def auth_delete(token, data):
    requests_auth(token, 'delete/', method='DELETE', data=data)


class IsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):

        json_data = auth_verify(request.headers.get('Authorization'))
        if json_data is None:
            return False

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
    try:
        return Users.objects.get(pk=id)
    except Users.DoesNotExist:
        raise serializers.ValidationError({'detail': 'User does not exist.'})


def validate_username(username, self_user):
    try:
        assert username is not None
        valide_username = Users.objects.get(username=username)
        assert valide_username.is_guest is False
        assert not valide_username.block.filter(blocked=self_user).exists()
    except (Users.DoesNotExist, AssertionError):
        raise serializers.ValidationError({'username': ['This user does not exist.']})
    return valide_username
