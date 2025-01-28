from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, APIException

from friends.serializers import FriendsSerializer
from friends.utils import get_friendship
from lib_transcendence import endpoints
from lib_transcendence.chat import AcceptChat
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.serializer import Serializer
from lib_transcendence.services import request_chat
from profile_pictures.create import create_user_profile_pictures
from stats.create import create_user_stats
from users.auth import auth_update
from users.models import Users
from users.serializers_utils import BaseUsersSerializer


class UsersMeSerializer(BaseUsersSerializer):
    accept_friend_request = serializers.BooleanField()
    notifications = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(max_length=50, write_only=True)
    old_password = serializers.CharField(max_length=50, write_only=True)
    trophies = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'is_guest',
            'profile_picture',
            'accept_friend_request',
            'accept_chat_from',
            'trophies',
            'created_at',
            'notifications',
            'is_online',
            'last_online',
            'password',
            'old_password',

        ]
        read_only_fields = [
            'id',
            'is_guest',
            'profile_picture',
            'trophies',
            'created_at',
            'notifications',
            'is_online',
            'last_online',
        ]

    @staticmethod
    def validate_accept_chat_from(value):
        return AcceptChat.validate(value)

    @staticmethod
    def get_notifications(obj):
        try:
            chat_notifications = request_chat(endpoints.Chat.fnotifications.format(user_id=obj.id), 'GET')['notifications']
        except APIException:
            chat_notifications = 0
        return {
            'friend_requests': obj.friend_requests_received.filter(new=True).count(),
            'chats': chat_notifications,
        }

    def update(self, instance, validated_data):
        if instance.is_guest and any([k != 'username' for k in validated_data]):
            raise PermissionDenied(MessagesException.PermissionDenied.GUEST_UPDATE_USERNAME)
        if 'username' in validated_data or 'password' in validated_data:
            auth_update(self.context['request'].headers.get('Authorization'), validated_data)
        validated_data.pop('password', None)
        return super().update(instance, validated_data)


class UsersSerializer(BaseUsersSerializer):
    status = serializers.SerializerMethodField(read_only=True)
    friends = FriendsSerializer(source='get_friends', read_only=True)
    trophies = serializers.SerializerMethodField(read_only=True)

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
            'status',
            'trophies',
            'friends',
        ]

    def get_friends(self, obj):
        request = self.context.get('request')
        if request is None or obj.id == request.user.id:
            return None
        return get_friendship(request.user.id, obj.id)


class ManageUserSerializer(Serializer):

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'is_guest',
        ]

    def create(self, validated_data):
        result = super().create(validated_data)
        create_user_stats(result)
        create_user_profile_pictures(result)
        return result
