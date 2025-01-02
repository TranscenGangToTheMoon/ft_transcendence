from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from lib_transcendence.exceptions import MessagesException


def is_guest(request):
    try:
        return request.data['auth_user']['is_guest']
    except KeyError:
        raise PermissionDenied()


class NotGuest(permissions.BasePermission):

    def has_permission(self, request, view):
        if is_guest(request):
            raise PermissionDenied(MessagesException.PermissionDenied.GUEST)
        return True


class GuestCannotDestroy(NotGuest):

    def has_permission(self, request, view):
        if is_guest(request) and request.method == 'DELETE':
            raise PermissionDenied(MessagesException.PermissionDenied.GUEST)
        return True


class GuestCannotCreate(NotGuest):

    def has_permission(self, request, view):
        if is_guest(request) and request.method == 'POST':
            raise PermissionDenied(MessagesException.PermissionDenied.GUEST)
        return True
