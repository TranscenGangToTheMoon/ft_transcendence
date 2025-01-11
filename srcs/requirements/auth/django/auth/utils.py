from lib_transcendence import endpoints
from lib_transcendence.exceptions import ServiceUnavailable, MessagesException
from lib_transcendence.services import request_users
from rest_framework.exceptions import APIException, AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed as JWTAuthenticationFailed

from guest.group import is_guest


def create_user_get_token(user, create=True):
    refresh_token = RefreshToken.for_user(user)
    token = {'access': str(refresh_token.access_token), 'refresh': str(refresh_token)}

    try:
        data = {'id': user.id, 'username': user.username, 'is_guest': is_guest(user=user)}
        request_users(endpoints.UsersManagement.manage_user, 'POST' if create else 'PATCH', data=data)
    except APIException:
        if create:
            user.delete()
        raise ServiceUnavailable('users')

    return token


class Authentication(JWTAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization', None)
        if token is None:
            raise AuthenticationFailed(MessagesException.Authentication.NOT_AUTHENTICATED)
        try:
            result = super().authenticate(request)
            if result is None:
                raise AuthenticationFailed(MessagesException.Authentication.AUTHENTICATION_FAILED)
            return result
        except JWTAuthenticationFailed as e:
            raise AuthenticationFailed({'detail': e.detail['detail'] + '.', 'code': e.detail['code']})
