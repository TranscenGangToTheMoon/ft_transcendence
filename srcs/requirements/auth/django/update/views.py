from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from lib_transcendence.exceptions import MessagesException

from guest.group import group_guests
from update.serializers import UpdateSerializer


class UpdateView(generics.UpdateAPIView):
    serializer_class = UpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        data = request.data
        password = data.get('password')
        if password is not None and request.user.groups.filter(name=group_guests).exists():
            raise PermissionDenied(MessagesException.PermissionDenied.GUEST_USERS_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


update_view = UpdateView.as_view()
