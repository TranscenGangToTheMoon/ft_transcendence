from rest_framework import serializers

from friend_requests.models import FriendRequests
from friends.models import Friends
from user_management.auth import get_user
from users.models import Users


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
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError({'error': 'Request is required.'})
        sender = get_user(request.user.id)

        if FriendRequests.objects.filter(sender=sender.pk).count() > 20:
            raise serializers.ValidationError({'error': 'You cannot send more than 20 friend requests at the same time.'})

        try:
            receiver = Users.objects.get(username=validated_data.pop('username'))
            assert not receiver.blocked_users.filter(pk=sender.pk).exists()
        except (Users.DoesNotExist, AssertionError):
            raise serializers.ValidationError({'username': ['This user does not exist.']})

        if receiver == sender:
            raise serializers.ValidationError({'username': ['You cannot send a friend request to yourself.']})

        if sender.blocked_users.filter(pk=receiver.pk).exists():
            raise serializers.ValidationError({'username': ['You block this user.']})

        if Friends.objects.filter(friends__in=[sender]).filter(friends__in=[receiver]).distinct().exists():
            raise serializers.ValidationError({'username': ['You are already friends with this user.']})

        if not receiver.accept_friend_request:
            raise serializers.ValidationError({'username': ['This user does not accept friend requests.']})

        if FriendRequests.objects.filter(sender=sender, receiver=receiver).exists():
            raise serializers.ValidationError({'username': ['You already send a friend requests.']})

        return super().create({'sender': sender, 'receiver': receiver})
