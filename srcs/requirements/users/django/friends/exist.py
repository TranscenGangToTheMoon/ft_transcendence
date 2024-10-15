from friends.models import Friends


def get_friendship(user1, user2):
    return Friends.objects.filter(friends__in=[user1]).filter(friends__in=[user2]).distinct().first()


def is_friendship(user1, user2):
    return get_friendship(user1, user2) is not None
