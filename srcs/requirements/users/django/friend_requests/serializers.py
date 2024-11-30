from lib_transcendence.exceptions import MessagesException, ResourceExists
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from friend_requests.models import FriendRequests
from friends.utils import is_friendship
from users.auth import get_user, get_valid_user
from users.serializers_utils import SmallUsersSerializer


class FriendRequestsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    sender = SmallUsersSerializer(read_only=True)
    receiver = SmallUsersSerializer(read_only=True)

    class Meta:
        model = FriendRequests
        fields = [
            'username',
            'id',
            'sender',
            'receiver',
            'send_at',
        ]

    def create(self, validated_data):
        sender = get_user(self.context.get('request'))
        receiver = get_valid_user(sender, username=validated_data.pop('username'))

        if receiver == sender:
            raise PermissionDenied(MessagesException.PermissionDenied.SEND_FRIEND_REQUEST_YOURSELF)

        if is_friendship(sender, receiver):
            raise ResourceExists(MessagesException.ResourceExists.FRIEND)

        if sender.friend_requests_sent.filter(receiver=receiver).exists():
            raise ResourceExists(MessagesException.ResourceExists.FRIEND_REQUEST_SENT)

        if receiver.friend_requests_sent.filter(receiver=sender).exists():
            raise ResourceExists(MessagesException.ResourceExists.FRIEND_REQUEST_RECEIVED)

        if sender.blocked.filter(blocked=receiver).exists():
            raise PermissionDenied(MessagesException.PermissionDenied.BLOCKED_USER)

        if sender.friend_requests_sent.count() > 20:
            raise PermissionDenied(MessagesException.PermissionDenied.SEND_MORE_THAN_20_FRIEND_REQUESTS)

        if not receiver.accept_friend_request:
            raise PermissionDenied(MessagesException.PermissionDenied.NOT_ACCEPT_FRIEND_REQUEST)

        return super().create({'sender': sender, 'receiver': receiver})
