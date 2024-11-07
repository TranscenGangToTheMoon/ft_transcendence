from lib_transcendence.exceptions import MessagesException
from lib_transcendence import endpoints
from rest_framework import serializers, permissions
from rest_framework.exceptions import PermissionDenied

from lib_transcendence.services import requests_users


class IsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        json_data = requests_users(endpoints.Users.me, 'GET', request)
        request.data['auth_user'] = json_data
        request.user.id = json_data['id']
        return True


class AllowedHostPermission(permissions.BasePermission):
    ALLOWED_HOSTS = ['game']

    def has_permission(self, request, view):
        host = request.get_host().split(':')[0]
        if host not in self.ALLOWED_HOSTS:
            raise PermissionDenied(
                detail="Authentication failed: Request must come from an authorized host."
            )
        return True


def get_auth_user(request=None):
    if request is None:
        raise serializers.ValidationError(MessagesException.ValidationError.REQUEST_REQUIRED)
    return request.data['auth_user']
