from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from game.request import requests_users


class IsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        json_data = requests_users(request, 'me/', 'GET')
        request.data['auth_user'] = json_data
        request.user.id = json_data['id']
        request.user.username = json_data['username']
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
