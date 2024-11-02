from lib_transcendence.request import request_service
from lib_transcendence.services import requests_matchmaking
from rest_framework import serializers

from block.models import Blocks
from friends.utils import get_friendship
from users.auth import get_user, validate_username


class BlockSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    blocked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Blocks
        fields = '__all__'

    @staticmethod
    def get_user(obj):
        return {'id': obj.user.id, 'username': obj.user.username}

    @staticmethod
    def get_blocked(obj):
        return {'id': obj.blocked.id, 'username': obj.blocked.username}

    def create(self, validated_data):
        user = get_user(self.context.get('request'))

        block_user = validate_username(validated_data.pop('username'), user)

        if block_user == user:
            raise serializers.ValidationError({'username': ['You cannot block yourself.']})

        if user.block.filter(blocked=block_user).exists():
            raise serializers.ValidationError({'username': ['You already block this user.']})

        def requests_chat(endpoint, method='GET', data=None):
            return request_service('chat', endpoint, method, data)

        requests_chat(
            endpoint=f'block-user/{block_user.id}/',
            method='DELETE',
        )

        requests_matchmaking(
            endpoint=f'block-user/{block_user.id}/',
            method='DELETE',
        )


        # todo remove chat
        # todo check remove from lobby

        friendship = get_friendship(user, block_user)
        if friendship:
            friendship.delete()
        user.sent_friend_requests.filter(receiver=block_user).delete()
        block_user.sent_friend_requests.filter(receiver=user).delete()
        validated_data['user'] = user
        validated_data['blocked'] = block_user
        return super().create(validated_data)
