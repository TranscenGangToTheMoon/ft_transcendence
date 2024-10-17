from rest_framework import permissions

from guest.group import group_guests


class IsNotAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsGuest(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.groups.filter(name=group_guests).exists()
