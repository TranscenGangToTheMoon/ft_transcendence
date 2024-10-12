import json

import requests
from rest_framework import generics
from rest_framework.exceptions import AuthenticationFailed

from users.models import Users
from users.serializers import UsersSerializer


# Create your views here.
class UsersMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UsersSerializer

    def get_object(self):
        token = self.request.headers.get('Authorization')

        # todo : pu in auth file and better throw erreur (en fonction du code d'erreur)
        if token is None:
            raise AuthenticationFailed('Authentication credentials were not provided.')

        try:
            response = requests.get(
                'http://auth:8000/api/auth/verify/',
                headers={
                    'Authorization': token,
                    'Content-Type': 'application/json'
                }
            )
            assert response.status_code == 200
            json_data = response.json()
        except (requests.ConnectionError, AssertionError, requests.exceptions.JSONDecodeError) as e:
            raise AuthenticationFailed('Failed to connect to auth service')

        # todo : update is_guest if needed
        try:
            user = Users.objects.get(id=json_data['id'])
            if user.is_guest != json_data['is_guest']:
                user.update(is_guest=json_data['is_guest'])
            return user
        except Users.DoesNotExist:
            print('creating user:', json_data, flush=True)
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
            token = request.headers.get('Authorization')
            try:
                assert token is not None;

                response = requests.patch(
                    'http://auth:8000/api/auth/update/',
                    headers={
                        'Authorization': token,
                        'Content-Type': 'application/json'
                    },
                    data=json.dumps(data),
                )
                assert response.status_code == 200
            except (requests.ConnectionError, AssertionError, requests.exceptions.JSONDecodeError) as e:
                raise AuthenticationFailed('Failed to connect to auth service')
        return super().update(request, *args, **kwargs)


users_me_view = UsersMeView.as_view()
