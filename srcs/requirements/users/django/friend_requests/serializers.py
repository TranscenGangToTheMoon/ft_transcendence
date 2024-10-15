from rest_framework import serializers

from block.models import Block
from friend_requests.models import FriendRequests
from friends.exist import is_friendship
from user_management.auth import get_user, validate_username


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

        if FriendRequests.objects.filter(sender=sender.pk).count() > 20:
            raise serializers.ValidationError({'error': 'You cannot send more than 20 friend requests at the same time.'})

        receiver = validate_username(validated_data.pop('username'), sender)

        if receiver == sender:
            raise serializers.ValidationError({'username': ['You cannot send a friend request to yourself.']})

        if Block.objects.filter(user=sender, blocked=receiver).exists():
            raise serializers.ValidationError({'username': ['You block this user.']})

        if is_friendship(sender, receiver):
            raise serializers.ValidationError({'username': ['You are already friends with this user.']})

        if not receiver.accept_friend_request:
            raise serializers.ValidationError({'username': ['This user does not accept friend requests.']})

        if FriendRequests.objects.filter(sender=sender, receiver=receiver).exists():
            raise serializers.ValidationError({'username': ['You already send a friend requests.']})

        return super().create({'sender': sender, 'receiver': receiver})
