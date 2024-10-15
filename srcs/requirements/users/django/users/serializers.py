from rest_framework import serializers

from friends.exist import get_friendship
from users.models import Users


class UsersSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    is_guest = serializers.BooleanField(read_only=True)
    profile_picture = serializers.IntegerField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    coins = serializers.IntegerField(read_only=True)
    trophy = serializers.IntegerField(read_only=True)
    current_rank = serializers.IntegerField(read_only=True)
    accept_friend_request = serializers.BooleanField(write_only=True)
    password = serializers.CharField(write_only=True)
    friends = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'is_guest',
            'profile_picture',
            'status',
            'coins',
            'trophy',
            'current_rank',
            'friends',
            'password',
            'accept_friend_request',
        ]

    def get_status(self, obj):
        return {
            'is_online': obj.is_online,
            'game_playing': obj.game_playing,
            'last_online': obj.last_online,
        }

    def get_friends(self, obj):
        request = self.context.get('request')
        if request is None or obj.id == request.user.id:
            return None
        friendship = get_friendship(request.user.id, obj.id)
        if friendship is None:
            return None
        return {'id': friendship.id, 'friends_since': friendship.friends_since}
