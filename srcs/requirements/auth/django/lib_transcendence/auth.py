import uuid
from abc import ABC, abstractmethod

from rest_framework import serializers
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, ParseError

from lib_transcendence.endpoints import Auth
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.services import request_auth


def get_user_from_auth(user_data):
    from django.contrib.auth.models import User

    try:
        return User.objects.get(id=user_data['id'])
    except User.DoesNotExist:
        return User.objects.create(id=user_data['id'], username=str(uuid.uuid1()))


class AbstractAuthentication(ABC, BaseAuthentication):
    @abstractmethod
    def auth_request(self, token):
        pass

    def authenticate(self, request):
        if not isinstance(request.data, dict):
            raise ParseError(MessagesException.ValidationError.DATA)

        token = request.headers.get('Authorization')

        if not token:
            token = request.query_params.get('token', None)
            if not token:
                raise NotAuthenticated(MessagesException.Authentication.NOT_AUTHENTICATED)
            token = 'Bearer ' + token

        try:
            json_data = self.auth_request(token)
        except AuthenticationFailed as e:
            if e.detail['code'] == MessagesException.Authentication.USER_NOT_FOUND['code']:
                raise AuthenticationFailed(MessagesException.Authentication.USER_NOT_FOUND)
            raise e
        if json_data is None:
            raise AuthenticationFailed(MessagesException.Authentication.AUTHENTICATION_FAILED)

        request.data['auth_user'] = json_data
        auth_user = get_user_from_auth(json_data)
        return auth_user, token

    def authenticate_header(self, request):
        return 'Bearer realm="api"'


class Authentication(AbstractAuthentication):

    def auth_request(self, token):
        return auth_verify(token)


def get_auth_token(request):
    token = request.headers.get('Authorization')
    if token is not None:
        return token
    raise NotAuthenticated(MessagesException.Authentication.NOT_AUTHENTICATED)


def get_auth_user(request=None):
    if request is None:
        raise serializers.ValidationError(MessagesException.ValidationError.REQUEST_REQUIRED)
    return request.data['auth_user']


def auth_verify(token=None, request=None):
    if request is not None:
        token = get_auth_token(request)
    elif token is None:
        raise NotAuthenticated(MessagesException.Authentication.NOT_AUTHENTICATED)
    return request_auth(token, Auth.verify, method='GET')
