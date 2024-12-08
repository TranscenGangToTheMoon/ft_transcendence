from lib_transcendence import endpoints
from lib_transcendence.Chat import AcceptChat
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.services import request_chat
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, APIException

from friends.serializers import FriendsSerializer
from friends.utils import get_friendship
from users.auth import auth_update
from users.models import Users


class UsersMeSerializer(serializers.ModelSerializer):
    accept_friend_request = serializers.BooleanField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'is_guest',
            'profile_picture',
            'accept_friend_request',
            'accept_chat_from',
            'coins',
            'trophies',
            'current_rank',
            'created_at',
            'password',

        ]
        read_only_fields = [
            'id',
            'is_guest',
            'profile_picture',
            'coins',
            'trophies',
            'current_rank',
            'created_at',
        ]

    @staticmethod
    def validate_accept_chat_from(value):
        return AcceptChat.validate(value)

    def update(self, instance, validated_data):
        if instance.is_guest and any([k != 'username' for k in validated_data]):
            raise PermissionDenied(MessagesException.PermissionDenied.GUEST_UPDATE_USERNAME)
        if 'username' in validated_data or 'password' in validated_data:
            auth_update(self.context['request'].headers.get('Authorization'), validated_data)
            if 'username' in validated_data and not instance.is_guest:
                try:
                    request_chat(endpoints.UsersManagement.frename_user.format(user_id=instance.id), data={'username': validated_data['username']})
                except APIException:
                    pass
        validated_data.pop('password', None)
        return super().update(instance, validated_data)


class UsersSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField(read_only=True)
    friends = FriendsSerializer(read_only=True)

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'is_guest',
            'profile_picture',
            'status',
            'trophies',
            'friends',
        ]
        read_only_fields = [
            'id',
            'username',
            'is_guest',
            'profile_picture',
            'current_rank',
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
        return friendship


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'is_guest',
        ]
