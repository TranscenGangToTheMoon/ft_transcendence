from lib_transcendence.exceptions import MessagesException, ResourceExists
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from friend_requests.models import FriendRequests
from friends.utils import is_friendship
from users.auth import get_user, validate_username


class FriendRequestsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    sender = serializers.CharField(source='sender.username', read_only=True)
    receiver = serializers.CharField(source='receiver.username', read_only=True)

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

        if sender.sent_friend_requests.count() > 20:
            raise PermissionDenied(MessagesException.PermissionDenied.SEND_MORE_THAN_20_FRIEND_REQUESTS)

        receiver = validate_username(validated_data.pop('username'), sender)

        if receiver == sender:
            raise PermissionDenied(MessagesException.PermissionDenied.SEND_FRIEND_REQUEST_YOURSELF)

        if sender.block.filter(blocked=receiver).exists():
            raise PermissionDenied(MessagesException.PermissionDenied.BLOCK_USER)

        if is_friendship(sender, receiver):
            raise ResourceExists(MessagesException.ResourceExists.FRIEND)

        if not receiver.accept_friend_request:
            raise PermissionDenied(MessagesException.PermissionDenied.NOT_ACCEPT_FRIEND_REQUEST)

        if sender.sent_friend_requests.filter(receiver=receiver).exists():
            raise ResourceExists(MessagesException.ResourceExists.FRIEND_REQUEST)

        return super().create({'sender': sender, 'receiver': receiver})
