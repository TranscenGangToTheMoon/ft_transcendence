from lib_transcendence.exceptions import MessagesException
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied

from friend_requests.models import FriendRequests
from friends.models import Friends
from users.auth import get_user
from users.serializers_utils import SmallUsersSerializer


class FriendsSerializer(serializers.ModelSerializer):
    friends = SmallUsersSerializer(many=True, read_only=True)

    class Meta:
        model = Friends
        fields = [
            'id',
            'friends',
            'friends_since',
            'matches_play_against',
            'user1_win',
            'matches_played_together',
            'matches_won_together',
        ]
        read_only_fields = [
            'id',
            'friends',
            'friends_since',
            'matches_play_against',
            'user1_win',
            'matches_played_together',
            'matches_won_together',
        ]

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
