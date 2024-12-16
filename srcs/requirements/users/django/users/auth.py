from lib_transcendence.exceptions import MessagesException
from lib_transcendence.services import request_auth
from lib_transcendence.endpoints import Auth
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied

from users.models import Users


def auth_update(token, data):
    return request_auth(token, Auth.update, method='PATCH', data=data)


def auth_delete(token, data):
    request_auth(token, Auth.delete, method='DELETE', data=data)


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
