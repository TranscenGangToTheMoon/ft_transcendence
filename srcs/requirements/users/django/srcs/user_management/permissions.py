from rest_framework import permissions

from user_management.auth import auth_verify


class IsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        auth_verify(request.headers.get('Authorization'))
        return True
