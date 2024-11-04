from rest_framework import generics
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed
from rest_framework.permissions import IsAuthenticated

from delete.serializers import DeleteSerializer


class DeleteView(generics.DestroyAPIView):
    serializer_class = DeleteSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        data = request.data
        password = data.get('password')
        if password is None:
            raise NotAuthenticated({'password': ['Password confirmation is required to delete the account.']})
        if not request.user.check_password(password):
            raise AuthenticationFailed({'password': ['Incorrect password.']})
        return super().delete(request, *args, **kwargs)


delete_view = DeleteView.as_view()
