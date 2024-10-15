from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from verify.serializers import VerrifyUserSerializer


# Create your views here.
class VerifyView(generics.RetrieveAPIView):
    serializer_class = VerrifyUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


token_verify = VerifyView.as_view()
