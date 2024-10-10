from rest_framework import generics

from auth.permissions import IsNotAuthenticated
from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsNotAuthenticated]


register = RegisterView.as_view()
