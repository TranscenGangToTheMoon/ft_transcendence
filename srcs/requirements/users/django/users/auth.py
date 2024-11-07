from typing import Literal

from lib_transcendence.exceptions import MessagesException
from lib_transcendence.request import request_service
from lib_transcendence.endpoints import Auth
from rest_framework import permissions, serializers
from rest_framework.exceptions import NotAuthenticated, NotFound

from users.models import Users


def requests_auth(token, endpoint: Literal['update/', 'verify/', 'delete/'], method: Literal['GET', 'PUT', 'PATCH', 'DELETE'], data=None):
    if token is None:
        raise NotAuthenticated()

    return request_service('auth', endpoint, method, data, token)


def auth_verify(token):
    return requests_auth(token, Auth.verify, method='GET')


def auth_update(token, data):
    return requests_auth(token, Auth.update, method='PATCH', data=data)


def auth_delete(token, data):
    requests_auth(token, Auth.delete, method='DELETE', data=data)


class IsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):

        json_data = auth_verify(request.headers.get('Authorization'))
        if json_data is None:
            return False

        try:
            # todo remake
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
            raise serializers.ValidationError(MessagesException.ValidationError.REQUEST_REQUIRED)
        id = request.user.id
    try:
        return Users.objects.get(pk=id)
    except Users.DoesNotExist:
        raise NotFound(MessagesException.NotFound.USER)


def get_valid_user(self, username):
    try:
        valide_user = Users.objects.get(username=username)
        assert valide_user.is_guest is False
        assert not valide_user.block.filter(blocked=self).exists()
    except Users.DoesNotExist:
        raise NotFound(MessagesException.NotFound.USER)
    return valide_user
