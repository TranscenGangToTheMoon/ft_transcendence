from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from lib_transcendence.exceptions import MessagesException
from users.auth import get_user


class NotInGame(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if get_user(request).game_playing is None:
            return True
        raise PermissionDenied(MessagesException.PermissionDenied.IN_GAME)
