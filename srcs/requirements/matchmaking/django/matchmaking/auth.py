from lib_transcendence import endpoints
from lib_transcendence.auth import AbstractAuthentication
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.services import request_users
from rest_framework.exceptions import AuthenticationFailed


class UserMeAuthentication(AbstractAuthentication):
    def auth_request(self, token):
        result = request_users(endpoints.Users.me, token=token)
        if not result['is_online']:
            raise AuthenticationFailed(MessagesException.AuthenticationFailed.NOT_CONNECTED_SSE)
        return result
