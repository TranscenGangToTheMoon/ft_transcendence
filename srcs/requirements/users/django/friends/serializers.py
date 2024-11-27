from lib_transcendence.exceptions import MessagesException
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied

from friend_requests.models import FriendRequests
from friends.models import Friends
from users.auth import get_user


class FriendsSerializer(serializers.ModelSerializer):
    friends = serializers.SerializerMethodField()

    class Meta:
        model = Friends
        fields = [
            'id',
            'friends',
            'friends_since',
            'matches_play_against',
            'user1_win', # todo remake
            'matches_play_together',
            'matches_win_together',
        ]

    @staticmethod
    def get_friends(obj):
        return [user.username for user in obj.friends.all()]

    def create(self, validated_data):
        user_accept = get_user(self.context.get('request'))

        if user_accept.friend_requests_sent.filter(id=self.context['friend_request_id']).exists():
            raise PermissionDenied(MessagesException.PermissionDenied.ACCEPT_FRIEND_REQUEST_YOURSELF)

        try:
            friend_request = user_accept.friend_requests_received.get(id=self.context['friend_request_id'])
            friend_request.delete()
        except FriendRequests.DoesNotExist:
            raise NotFound(MessagesException.NotFound.FRIEND_REQUEST)

        result = super().create(validated_data)
        result.friends.add(user_accept, friend_request.sender)
        return result
