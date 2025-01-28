from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from guest.group import is_guest
from lib_transcendence.exceptions import MessagesException


class IsNotAuthenticated(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            raise PermissionDenied(MessagesException.PermissionDenied.ALREADY_AUTHENTICATED)
        return True


class IsGuest(BasePermission):

    def has_permission(self, request, view):
        if not is_guest(request):
            raise PermissionDenied(MessagesException.PermissionDenied.GUEST_REQUIRED)
        return True
