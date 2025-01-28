from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from guest.group import is_guest
from lib_transcendence.exceptions import MessagesException
from update.serializers import UpdateSerializer


class UpdateUserView(generics.UpdateAPIView):
    serializer_class = UpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        data = request.data
        password = data.get('password')
        if password is not None and is_guest(request):
            raise PermissionDenied(MessagesException.PermissionDenied.GUEST_UPDATE_USERNAME)
        return super().update(request, *args, **kwargs)


update_user_view = UpdateUserView.as_view()
