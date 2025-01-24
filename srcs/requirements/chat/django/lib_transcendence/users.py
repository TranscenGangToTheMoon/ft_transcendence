from django.utils.deprecation import MiddlewareMixin
from lib_transcendence import endpoints
from lib_transcendence.services import request_users
from lib_transcendence.exceptions import MessagesException
from rest_framework.exceptions import NotFound


def retrieve_users(user_id: list[int] | int, return_type=list):
    if isinstance(user_id, int):
        user_ids = [user_id]
    else:
        user_ids = user_id
    response = request_users(endpoints.Users.users, 'GET', data={'user_ids': user_ids})
    if len(response) == 0:
        raise NotFound(MessagesException.NotFound.USERS)
    if return_type is list:
        return response
    result = {}
    for user in response:
        result[user['id']] = user
    return result


class DeleteTempUserMiddleware(MiddlewareMixin):
    @staticmethod
    def process_response(request, response):
        if not request.user.is_anonymous:
            request.user.delete()
        return response
