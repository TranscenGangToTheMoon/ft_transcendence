from rest_framework import generics

from auth.permissions import IsNotAuthenticated
from guest.serializers import GuestTokenSerializer


class OptainGuestTokenView(generics.CreateAPIView):
    serializer_class = GuestTokenSerializer
    permission_classes = [IsNotAuthenticated]


optain_guest_token_view = OptainGuestTokenView.as_view()
