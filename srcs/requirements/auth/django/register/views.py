from lib_transcendence.exceptions import MessagesException
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from guest.group import is_guest
from register.serializers import RegisterSerializer


class GuestRequiredPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and is_guest(request)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    authentication_classes = []


class RegisterGuestView(generics.UpdateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [GuestRequiredPermission]

    def get_object(self):
        return self.request.user


register_view = RegisterView.as_view()
register_guest_view = RegisterGuestView.as_view()
