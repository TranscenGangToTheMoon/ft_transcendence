from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import NotFound

from lib_transcendence import endpoints
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.services import request_users


def retrieve_users(user_id: list[int] | int, return_type=list, size='small') -> dict | list:
    if isinstance(user_id, int):
        user_ids = [user_id]
    else:
        user_ids = user_id
    response = request_users(endpoints.Users.users, 'GET', data={'user_ids': user_ids, 'size': size})
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
