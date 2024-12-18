from lib_transcendence import endpoints
from lib_transcendence.services import request_users
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.tokens import RefreshToken

from guest.group import is_guest


def create_user_get_token(user, create=True):
    refresh_token = RefreshToken.for_user(user)
    token = {'access': str(refresh_token.access_token), 'refresh': str(refresh_token)}

    try:
        data = {'id': user.id, 'username': user.username, 'is_guest': is_guest(user=user)}
        request_users(endpoints.UsersManagement.manage_user, method='POST' if create else 'PATCH', data=data)
    except APIException:
        if create:
            user.delete()
        raise APIException

    return token
