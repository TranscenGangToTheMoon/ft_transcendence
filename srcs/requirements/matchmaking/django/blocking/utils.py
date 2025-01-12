from django.db.models import Q
from lib_transcendence import endpoints
from lib_transcendence.pagination import get_all_pagination_items
from lib_transcendence.services import request_users

from blocking.models import Blocked


def create_player_instance(request, instance=None, *args, **kwargs):
    result = get_all_pagination_items(request_users, 'users', endpoints.Users.blocked, request=request)
    for blocked_instance in result:
        Blocked.objects.create(user_id=request.user.id, blocked_user_id=blocked_instance['blocked']['id'])

    if instance is not None:
        return instance.objects.create(*args, **kwargs)


def delete_player_instance(user_id=None):
    Blocked.objects.filter(user_id=user_id).delete()


def are_users_blocked(user1, user2):
    return Blocked.objects.filter(
        Q(user_id=user1, blocked_user_id=user2) |
        Q(user_id=user2, blocked_user_id=user1)
    ).exists()
