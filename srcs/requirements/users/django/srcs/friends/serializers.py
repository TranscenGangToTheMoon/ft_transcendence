from rest_framework import serializers

from friend_requests.models import FriendRequests
from friends.models import Friends
from user_management.auth import get_user, validate_username
from users.models import Users


class FriendsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    friends = serializers.SerializerMethodField()

    class Meta:
        model = Friends
        fields = [
            'username',
            'id',
            'friends',
            'friends_since',
            'matches_play_against',
            'user1_win',
            'matches_play_together',
            'matches_win_together',
        ]

    def get_friends(self, obj):
        return [user.username for user in obj.friends.all()]

    def create(self, validated_data):
        user_accept = get_user(self.context.get('request'))
        user_send_friend_request = validate_username(validated_data.pop('username'), user_accept)

        if Friends.objects.filter(friends__in=[user_accept]).filter(friends__in=[user_send_friend_request]).distinct().exists():
            raise serializers.ValidationError({'username': ['You are already friends with this user.']})

        try:
            friend_request = FriendRequests.objects.get(sender=user_send_friend_request, receiver=user_accept)
            friend_request.delete()
        except FriendRequests.DoesNotExist:
            raise serializers.ValidationError({'username': ['No friend request exists with this user.']})

        result = super().create(validated_data)
        result.friends.add(user_accept, user_send_friend_request)
        return result
