from lib_transcendence.exceptions import MessagesException
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from guest.group import is_guest
from register.serializers import RegisterSerializer


class RegisterView(generics.UpdateAPIView, generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def get_object(self):
        return self.request.user


register_view = RegisterView.as_view()
