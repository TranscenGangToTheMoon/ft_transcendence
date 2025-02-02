from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from friend_requests.models import FriendRequests
from friends.utils import is_friendship
from lib_transcendence.exceptions import MessagesException, ResourceExists
from lib_transcendence.serializer import Serializer
from users.auth import get_user, get_valid_user
from users.serializers_utils import SmallUsersSerializer


class FriendRequestsSerializer(Serializer):
    username = serializers.CharField(max_length=15, write_only=True)
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
            'new',
        ]
        read_only_fields = [
            'id',
            'sender',
            'receiver',
            'send_at',
            'new',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        user = get_user(self.context.get('request'))
        if user.id != instance.receiver.id:
            representation.pop('new', None)
        return representation

    def create(self, validated_data):
        sender = get_user(self.context.get('request'))

        receiver = get_valid_user(sender, self_blocked=True, username=validated_data.pop('username'))

        if receiver == sender:
            raise PermissionDenied(MessagesException.PermissionDenied.SEND_FRIEND_REQUEST_YOURSELF)

        if is_friendship(sender, receiver):
            raise ResourceExists(MessagesException.ResourceExists.FRIEND)

        if sender.friend_requests_sent.filter(receiver=receiver).exists():
            raise ResourceExists(MessagesException.ResourceExists.FRIEND_REQUEST_SENT)

        if receiver.friend_requests_sent.filter(receiver=sender).exists():
            raise ResourceExists(MessagesException.ResourceExists.FRIEND_REQUEST_RECEIVED)

        if sender.friend_requests_sent.count() > 20:
            raise PermissionDenied(MessagesException.PermissionDenied.SEND_MORE_THAN_20_FRIEND_REQUESTS)

        if not receiver.accept_friend_request:
            raise PermissionDenied(MessagesException.PermissionDenied.NOT_ACCEPT_FRIEND_REQUEST)

        return super().create({'sender': sender, 'receiver': receiver})
