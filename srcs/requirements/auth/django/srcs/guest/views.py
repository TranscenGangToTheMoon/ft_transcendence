from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from auth.permissions import IsNotAuthenticated, IsGuest
from guest.serializers import GuestTokenSerializer, GuestRegisterSerializer


class GuestTokenView(generics.CreateAPIView):
    serializer_class = GuestTokenSerializer
    permission_classes = [IsNotAuthenticated]


class GuestRegisterView(generics.UpdateAPIView):
    serializer_class = GuestRegisterSerializer
    permission_classes = [IsAuthenticated, IsGuest]

    def get_object(self):
        return self.request.user


guest_token = GuestTokenView.as_view()
guest_register = GuestRegisterView.as_view()
