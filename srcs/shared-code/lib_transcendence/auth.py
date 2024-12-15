from lib_transcendence.endpoints import Auth
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.services import request_users, request_auth, get_auth_token
from rest_framework import serializers
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import ParseError


#todo delete user after request
def get_user_from_auth(user_data):
    from django.contrib.auth.models import User

    user, created = User.objects.get_or_create(id=user_data['id'])
    if user.username != user_data['username']:
        user.username = user_data['username']
        user.save()
    return user


class Authentication(BaseAuthentication):
    def authenticate(self, request):
        if type(request.data) is not dict:
            raise ParseError(MessagesException.ValidationError.REQUEST_DATA_REQUIRED)
        json_data = auth_verify(request=request)
        # json_data = request_users(endpoints.Users.me, 'GET', request)
        request.data['auth_user'] = json_data
        user = get_user_from_auth(json_data)

        return user, None

    def authenticate_header(self, request):
        return 'Bearer realm="api"'


def get_auth_user(request=None):
    if request is None:
        raise serializers.ValidationError(MessagesException.ValidationError.REQUEST_REQUIRED)
    return request.data['auth_user']


def auth_verify(token=None, request=None):
    if request is not None:
        token = get_auth_token(request)
    return request_auth(token, Auth.verify, method='GET')
