from lib_transcendence.exceptions import MessagesException, ResourceExists
from lib_transcendence.services import requests_chat, requests_matchmaking
from lib_transcendence import endpoints
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, NotFound

from block.models import Blocks
from friends.utils import get_friendship
from users.auth import get_user, get_valide_user


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

        block_user = get_valide_user(user, validated_data.pop('username'))

        if block_user.id == user.id:
            raise PermissionDenied(MessagesException.PermissionDenied.BLOCK_YOURSELF)

        if user.block.filter(blocked=block_user).exists():
            raise ResourceExists(MessagesException.ResourceExists.BLOCK)

        endpoint = endpoints.UsersManagement.fblocked_user.format(user_id=user.id, block_user_id=block_user.id)
        try:
            requests_chat(
                endpoint=endpoint,
                data={'blocked': True},
            )
        except NotFound:
            pass

        try:
            requests_matchmaking(
                endpoint=endpoint,
                method='DELETE',
            )
        except NotFound:
            pass

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
