from rest_framework import generics
from rest_framework.exceptions import ValidationError

from user_management.auth import auth_update, auth_delete
from user_management.permissions import get_object
from users.serializers import UsersSerializer


class UsersMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UsersSerializer

    def get_object(self):
        return get_object(self.request)

    def update(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.pop('password', None)
        data = {}
        if username is not None:
            data['username'] = username
        if password is not None:
            data['password'] = password
        if data:
            auth_update(request.headers.get('Authorization'), data)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        result = super().destroy(request, *args, **kwargs)
        password = self.request.data.get('password')
        if password is None:
            raise ValidationError({'password': 'Password confirmation is required to delete the account.'})
        auth_delete(self.request.headers.get('Authorization'), {'password': password})
        return result


users_me_view = UsersMeView.as_view()
