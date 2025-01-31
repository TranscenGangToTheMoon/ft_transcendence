from django.db import IntegrityError
from django.db.models import Q

from blocking.models import Blocked
from lib_transcendence import endpoints
from lib_transcendence.auth import get_auth_token
from lib_transcendence.exceptions import Throttled
from lib_transcendence.pagination import get_all_pagination_items
from lib_transcendence.services import request_users


def model_exists(model, user_id):
    return model.objects.filter(user_id=user_id).exists()


def create_blocked(user_id, blocked=None, request=None):
    if not model_exists(Blocked, user_id):
        if blocked is None:
            blocked = get_all_pagination_items(request_users, 'users', endpoints.Users.blocked, token=get_auth_token(request))
        for blocked_instance in blocked:
            Blocked.objects.create(user_id=user_id, blocked_user_id=blocked_instance['blocked']['id'])


def create_player_instance(user, instance=None, *args, **kwargs):
    create_blocked(user['id'], user['blocked'])

    if instance is not None:
        try:
            return instance.objects.create(*args, **kwargs)
        except IntegrityError:
            raise Throttled()


def delete_player_instance(user_id=None):
    Blocked.objects.filter(user_id=user_id).delete()


def are_users_blocked(user1, user2):
    return Blocked.objects.filter(
        Q(user_id=user1, blocked_user_id=user2) |
        Q(user_id=user2, blocked_user_id=user1)
    ).exists()
