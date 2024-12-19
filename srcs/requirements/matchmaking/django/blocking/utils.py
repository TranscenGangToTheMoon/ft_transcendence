from django.db.models import Q
from lib_transcendence import endpoints
from lib_transcendence.exceptions import ServiceUnavailable
from lib_transcendence.services import request_users
from rest_framework.exceptions import APIException

from blocking.models import Blocked


def create_player_instance(request, instance=None, *args, **kwargs):
    while True:
        try:
            result = request_users(endpoints.Users.blocked, method='GET', request=request)
            for blocked_instance in result['results']:
                Blocked.objects.create(user_id=blocked_instance['user']['id'], blocked_user_id=blocked_instance['blocked']['id'])
            if result['next'] is None:
                break
        except APIException:
            raise ServiceUnavailable('users')

    if instance is not None:
        return instance.objects.create(*args, **kwargs)


def delete_player_instance(user_id=None):
    Blocked.objects.filter(user_id=user_id).delete()


def are_users_blocked(user1, user2):
    return Blocked.objects.filter(
        Q(user_id=user1, blocked_user_id=user2) |
        Q(user_id=user2, blocked_user_id=user1)
    ).exists()
