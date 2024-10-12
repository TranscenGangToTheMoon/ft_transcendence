from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from user_management.auth import auth_verify, auth_update, auth_delete
from users.models import Users
from users.serializers import UsersSerializer


class UsersMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UsersSerializer

    def get_object(self):
        json_data = auth_verify(self.request.headers.get('Authorization'))

        try:
            user = Users.objects.get(id=json_data['id'])
            if user.is_guest != json_data['is_guest']:
                user.update(is_guest=json_data['is_guest'])
            return user
        except Users.DoesNotExist:
            return Users.objects.create(**json_data)

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
