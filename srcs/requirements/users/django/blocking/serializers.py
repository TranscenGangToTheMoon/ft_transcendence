from lib_transcendence.exceptions import MessagesException, ResourceExists
from lib_transcendence.sse_events import EventCode
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from lib_transcendence.serializer import Serializer

from blocking.models import BlockedUsers
from friends.utils import get_friendship
from friend_requests.models import FriendRequests
from sse.events import publish_event
from users.auth import get_user, get_valid_user
from users.serializers_utils import SmallUsersSerializer


class BlockedSerializer(Serializer):
    user_id = serializers.IntegerField(write_only=True)
    blocked = SmallUsersSerializer(read_only=True)

    class Meta:
        model = BlockedUsers
        fields = [
            'user_id',
            'id',
            'blocked',
            'blocked_at',
        ]

    @staticmethod
    def get_blocked(obj):
        return {'id': obj.blocked.id, 'username': obj.blocked.username}

    def create(self, validated_data):
        user = get_user(self.context.get('request'))

        if user.blocked.count() >= 50:
            raise PermissionDenied(MessagesException.PermissionDenied.BLOCK_MORE_THAN_50_USERS)

        blocked_user = get_valid_user(user, id=validated_data.pop('user_id'))

        if blocked_user.id == user.id:
            raise PermissionDenied(MessagesException.PermissionDenied.BLOCK_YOURSELF)

        if user.blocked.filter(blocked=blocked_user).exists():
            raise ResourceExists(MessagesException.ResourceExists.BLOCK)

        friendship = get_friendship(user, blocked_user)
        if friendship:
            publish_event([friendship.user_1, friendship.user_2], EventCode.DELETE_FRIEND, {'id': friendship.id})
            friendship.delete()

        for user1, user2 in ((user, blocked_user), (blocked_user, user)):
            try:
                instance = user1.friend_requests_sent.get(receiver=user2)
                publish_event(user1, EventCode.REJECT_FRIEND_REQUEST, {'id': instance.id})
                publish_event(user2, EventCode.CANCEL_FRIEND_REQUEST, {'id': instance.id})
                instance.delete()
            except FriendRequests.DoesNotExist:
                pass

        validated_data['user'] = user
        validated_data['blocked'] = blocked_user
        result = super().create(validated_data)
        result.blocked_services()
        return result
