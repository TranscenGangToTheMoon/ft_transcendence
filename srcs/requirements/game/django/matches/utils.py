from lib_transcendence import endpoints
from lib_transcendence.exceptions import ServiceUnavailable
from lib_transcendence.services import request_users
from rest_framework.exceptions import APIException


def send_match_result(match):
    try:
        from matches.serializers import MatchSerializer

        request_users(endpoints.Users.result_match, 'POST', data=MatchSerializer(match).data)
    except APIException:
        raise ServiceUnavailable('users')
