from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from verify.serializers import VerifyUserSerializer


class VerifyTokenView(generics.RetrieveAPIView):
    serializer_class = VerifyUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


verify_token_view = VerifyTokenView.as_view()
