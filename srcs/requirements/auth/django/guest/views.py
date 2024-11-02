from rest_framework import generics

from auth.permissions import IsNotAuthenticated
from guest.serializers import GuestTokenSerializer


class GuestTokenView(generics.CreateAPIView):
    serializer_class = GuestTokenSerializer
    permission_classes = [IsNotAuthenticated]


guest_token = GuestTokenView.as_view()
