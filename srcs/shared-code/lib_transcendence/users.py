from django.utils.deprecation import MiddlewareMixin
from lib_transcendence import endpoints
from lib_transcendence.services import request_users


def retrieve_users(user_id: list[int] | int, request):
    if isinstance(user_id, int):
        user_ids = [user_id]
    else:
        user_ids = user_id
    return request_users(endpoints.Users.users, 'GET', request, {'user_ids': user_ids})


class DeleteTempUserMiddleware(MiddlewareMixin):
    @staticmethod
    def process_response(request, response):
        if not request.user.is_anonymous:
            request.user.delete()
        return response
