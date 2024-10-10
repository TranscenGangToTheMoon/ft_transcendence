import requests
from rest_framework import generics
from rest_framework.exceptions import AuthenticationFailed

from users.models import Users
from users.serializers import UsersMeSerializer


# Create your views here.
class UsersMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UsersMeSerializer

    def get_object(self):
        token = self.request.headers.get('Authorization')

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

        try:
            user = Users.objects.get(id=json_data['id'])
            return user
        except Users.DoesNotExist:
            print('creating user:', json_data, flush=True)
            return Users.objects.create(**json_data)


users_me = UsersMeView.as_view()
