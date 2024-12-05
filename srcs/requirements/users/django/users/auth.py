from lib_transcendence.exceptions import MessagesException
from lib_transcendence.services import requests_auth
from lib_transcendence.auth import auth_verify
from lib_transcendence.endpoints import Auth
from rest_framework import serializers
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import NotFound, PermissionDenied

from users.models import Users


def auth_update(token, data):
    return requests_auth(token, Auth.update, method='PATCH', data=data)


def auth_delete(token, data):
    requests_auth(token, Auth.delete, method='DELETE', data=data)


class Authentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')

        if not token:
            return None

        json_data = auth_verify(token)
        if json_data is None:
            return None

        try:
            # todo remake
            # 1. todo REMAKE not permision but authenticaed error
            # 2. USE authenticatd classes not permision // change all
            print('CACA json_data', json_data, flush=True)
            user = Users.objects.get(id=json_data['id'])
            if user.is_guest != json_data['is_guest']:
                user.is_guest = json_data['is_guest']
                user.save()
            if user.username != json_data['username']:
                user.username = json_data['username']
                user.save()
        except Users.DoesNotExist:
            user = Users.objects.create(**json_data) # todo remake

        return user, token


def get_user(request=None, id=None):
    if id is None:
        if request is None:
            raise serializers.ValidationError(MessagesException.ValidationError.REQUEST_REQUIRED)
        id = request.user.id
    try:
        return Users.objects.get(id=id)
    except Users.DoesNotExist:
        raise NotFound(MessagesException.NotFound.USER)


def get_valid_user(self, assert_guest=True, self_blocked=False, **kwargs):
    try:
        valide_user = Users.objects.get(**kwargs)
        if assert_guest:
            assert valide_user.is_guest is False
        if self_blocked:
            if self.blocked.filter(blocked=valide_user).exists():
                raise PermissionDenied(MessagesException.PermissionDenied.BLOCKED_USER)
        assert not valide_user.blocked.filter(blocked=self).exists()
    except (Users.DoesNotExist, AssertionError):
        raise NotFound(MessagesException.NotFound.USER)
    return valide_user
