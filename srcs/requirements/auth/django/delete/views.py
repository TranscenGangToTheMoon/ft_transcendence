from rest_framework import generics
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from lib_transcendence.exceptions import MessagesException


class DeleteUserView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        data = request.data
        password = data.get('password')
        if password is None:
            raise NotAuthenticated({'password': [MessagesException.Authentication.PASSWORD_CONFIRMATION_REQUIRED]})
        if not request.user.check_password(password):
            raise AuthenticationFailed({'password': [MessagesException.Authentication.INCORRECT_PASSWORD]})
        return super().delete(request, *args, **kwargs)


delete_user_view = DeleteUserView.as_view()
