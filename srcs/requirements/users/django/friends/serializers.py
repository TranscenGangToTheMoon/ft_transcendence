from rest_framework import serializers

from friend_requests.models import FriendRequests
from friends.utils import is_friendship
from friends.models import Friends
from users.auth import get_user, validate_username


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

    @staticmethod
    def get_friends(obj):
        return [user.username for user in obj.friends.all()]

    def create(self, validated_data):
        user_accept = get_user(self.context.get('request'))
        user_send_friend_request = validate_username(validated_data.pop('username'), user_accept)

        if is_friendship(user_accept, user_send_friend_request):
            raise serializers.ValidationError({'username': ['You are already friends with this user.']})

        try:
            user_accept.received_friend_requests.get(sender=user_send_friend_request).delete()
        except FriendRequests.DoesNotExist:
            raise serializers.ValidationError({'username': ['No friend request exists with this user.']})

        result = super().create(validated_data)
        result.friends.add(user_accept, user_send_friend_request)
        return result
