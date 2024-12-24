from abc import ABC, abstractmethod

from lib_transcendence.endpoints import Auth
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.services import request_auth, get_auth_token
from rest_framework import serializers
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated


def get_user_from_auth(user_data):
    from django.contrib.auth.models import User

    user, created = User.objects.get_or_create(id=user_data['id'])
    if user.username != user_data['username']:
        user.username = user_data['username']
        user.save()
    return user


class AbstractAuthentication(ABC, BaseAuthentication):
    @abstractmethod
    def auth_request(self, token):
        pass

    def authenticate(self, request):
        token = request.headers.get('Authorization')

        if not token:
            raise NotAuthenticated()

        try:
            json_data = self.auth_request(token)
        except AuthenticationFailed as e:
            raise e
        if json_data is None:
            raise AuthenticationFailed()

        request.data['auth_user'] = json_data
        auth_user = get_user_from_auth(json_data)
        return auth_user, token

    def authenticate_header(self, request):
        return 'Bearer realm="api"'


class Authentication(AbstractAuthentication):
    def auth_request(self, token):
        return auth_verify(token)


def get_auth_user(request=None):
    if request is None:
        raise serializers.ValidationError(MessagesException.ValidationError.REQUEST_REQUIRED)
    return request.data['auth_user']


def auth_verify(token=None, request=None):
    if request is not None:
        token = get_auth_token(request)
    return request_auth(token, Auth.verify, method='GET')
