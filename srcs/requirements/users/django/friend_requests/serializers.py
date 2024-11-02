from rest_framework import serializers

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
            raise serializers.ValidationError({'detail': 'You cannot send more than 20 friend requests at the same time.'})

        receiver = validate_username(validated_data.pop('username'), sender)

        if receiver == sender:
            raise serializers.ValidationError({'username': ['You cannot send a friend request to yourself.']})

        if sender.block.filter(blocked=receiver).exists():
            raise serializers.ValidationError({'username': ['You block this user.']})

        if is_friendship(sender, receiver):
            raise serializers.ValidationError({'username': ['You are already friends with this user.']})

        if not receiver.accept_friend_request:
            raise serializers.ValidationError({'username': ['This user does not accept friend requests.']})

        if sender.sent_friend_requests.filter(receiver=receiver).exists():
            raise serializers.ValidationError({'username': ['You already send a friend requests to this user.']})

        return super().create({'sender': sender, 'receiver': receiver})
