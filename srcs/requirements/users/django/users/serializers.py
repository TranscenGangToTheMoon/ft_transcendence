from lib_transcendence.Chat import AcceptChat
from rest_framework import serializers

from friends.utils import get_friendship
from users.auth import auth_update
from users.models import Users


class UsersSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField(read_only=True)
    current_rank = serializers.IntegerField(read_only=True)
    accept_friend_request = serializers.BooleanField(write_only=True)
    accept_chat_state = serializers.IntegerField(write_only=True)
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
            'trophies',
            'current_rank',
            'friends',
            'password',
            'accept_friend_request',
            'accept_chat_from',
        ]
        read_only_fields = [
            'id',
            'is_guest',
            'profile_picture',
            'status',
            'coins',
            'trophies',
            'current_rank',
            'friends'
        ]

    @staticmethod
    def get_status(obj):
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

    @staticmethod
    def validate_accept_chat_from(value):
        return AcceptChat.validate(value)

    def update(self, instance, validated_data):
        if instance.is_guest and any([k != 'username' for k in validated_data]):
            raise serializers.ValidationError({'detail': 'Guest users can only update their username.'})
        if 'username' in validated_data or 'password' in validated_data:
            auth_update(self.context['request'].headers.get('Authorization'), validated_data)
        return super().update(instance, validated_data)
