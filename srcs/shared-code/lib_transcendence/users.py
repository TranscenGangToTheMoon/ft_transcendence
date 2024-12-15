from lib_transcendence import endpoints
from lib_transcendence.services import request_users


def retrieve_users(user_id: list[int] | int, request):
    if isinstance(user_id, int):
        user_ids = [user_id]
    else:
        user_ids = user_id
    return request_users(endpoints.Users.users, 'GET', request, {'user_ids': [89849889, 194894]})
