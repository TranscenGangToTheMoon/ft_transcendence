from django.db.models import Q
from rest_framework.views import APIView

from friends.models import Friends


def get_friendship(user1, user2):
    return Friends.objects.filter(Q(user_1=user1, user_2=user2) | Q(user_1=user2, user_2=user1)).first()


def is_friendship(user1, user2):
    return get_friendship(user1, user2) is not None


def get_friend(friendship, user):
    if friendship.user_1.id == user.id:
        return friendship.user_2
    return friendship.user_1


class SerializerFriendContext(APIView):

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user.id
        return context
