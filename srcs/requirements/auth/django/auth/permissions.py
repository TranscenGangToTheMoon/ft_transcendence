from rest_framework import permissions

from guest.group import is_guest


class IsNotAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsGuest(permissions.BasePermission):

    def has_permission(self, request, view):
        return is_guest(request)
