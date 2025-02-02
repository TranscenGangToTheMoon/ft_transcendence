from rest_framework.exceptions import AuthenticationFailed

from lib_transcendence import endpoints
from lib_transcendence.auth import AbstractAuthentication
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.services import request_users


class UserAuthAuthentication(AbstractAuthentication):

    def auth_request(self, token):
        result = request_users(endpoints.Users.auth_matchmaking, 'GET', token=token)
        if not result['is_online']:
            raise AuthenticationFailed(MessagesException.Authentication.NOT_CONNECTED_SSE)
        return result
