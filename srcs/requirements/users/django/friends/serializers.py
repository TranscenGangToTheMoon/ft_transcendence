from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied

from friend_requests.models import FriendRequests
from friends.models import Friends
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.serializer import Serializer
from users.auth import get_user
from users.serializers_utils import LargeUsersSerializer


class FriendsSerializer(Serializer):
    friend = serializers.ModelSerializer(read_only=True)
    friend_win = serializers.ModelSerializer(read_only=True)
    me_win = serializers.ModelSerializer(read_only=True)

    class Meta:
        model = Friends
        fields = [
            'id',
            'friend',
            'friend_win',
            'me_win',
            'friends_since',
            'matches_play_against',
            'matches_played_together',
            'matches_won_together',
        ]
        read_only_fields = [
            'id',
            'friend',
            'friend_win',
            'me_win',
            'friends_since',
            'matches_play_against',
            'matches_played_together',
            'matches_won_together',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.user_1.id == self.context['user']:
            data['friend_win'] = instance.user2_wins
            data['me_win'] = instance.user1_wins
            friend = instance.user_2
        else:
            data['friend_win'] = instance.user1_wins
            data['me_win'] = instance.user2_wins
            friend = instance.user_1
        data['friend'] = LargeUsersSerializer(friend).data
        return data

    def create(self, validated_data):
        user_accept = get_user(self.context.get('request'))
        fr_id = self.context.get('friend_request_id')

        if user_accept.friend_requests_sent.filter(id=fr_id).exists():
            raise PermissionDenied(MessagesException.PermissionDenied.ACCEPT_FRIEND_REQUEST_YOURSELF)

        try:
            friend_request = user_accept.friend_requests_received.get(id=fr_id)
            friend_request.delete()
        except FriendRequests.DoesNotExist:
            raise NotFound(MessagesException.NotFound.FRIEND_REQUEST)

        validated_data['id'] = fr_id
        validated_data['user_1'] = friend_request.sender
        validated_data['user_2'] = user_accept
        return super().create(validated_data)
