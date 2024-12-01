from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from auth.permissions import IsGuest
from register.serializers import RegisterSerializer


class RegisterGuestView(generics.UpdateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated, IsGuest]

    def get_object(self):
        return self.request.user


register_guest_view = RegisterGuestView.as_view()
