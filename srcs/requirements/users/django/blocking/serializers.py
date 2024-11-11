from lib_transcendence.exceptions import MessagesException, ResourceExists
from lib_transcendence.services import request_chat, request_matchmaking
from lib_transcendence import endpoints
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, NotFound

from blocking.models import BlockedUsers
from friends.utils import get_friendship
from users.auth import get_user, get_valid_user


class BlockedSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True) # todo change to user_id
    user = serializers.SerializerMethodField(read_only=True)
    blocked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BlockedUsers
        fields = '__all__'

    @staticmethod
    def get_user(obj):
        return {'id': obj.user.id, 'username': obj.user.username}

    @staticmethod
    def get_blocked(obj):
        return {'id': obj.blocked.id, 'username': obj.blocked.username}

    def create(self, validated_data):
        user = get_user(self.context.get('request'))

        if user.blocked.count() >= 50:
            raise PermissionDenied(MessagesException.PermissionDenied.BLOCK_MORE_THAN_50_USERS)

        blocked_user = get_valid_user(user, validated_data.pop('username'))

        if blocked_user.id == user.id:
            raise PermissionDenied(MessagesException.PermissionDenied.BLOCK_YOURSELF)

        if user.blocked.filter(blocked=blocked_user).exists():
            raise ResourceExists(MessagesException.ResourceExists.BLOCK)

        endpoint = endpoints.UsersManagement.fblocked_user.format(user_id=user.id, blocked_user_id=blocked_user.id)
        try:
            request_chat(
                endpoint=endpoint,
                data={'blocked': True},
            )
        except NotFound:
            pass

        try:
            request_matchmaking(
                endpoint=endpoint,
                method='DELETE',
            )
        except NotFound:
            pass

        # todo remove chat
        # todo check remove from lobby

        friendship = get_friendship(user, blocked_user)
        if friendship:
            friendship.delete()
        user.sent_friend_requests.filter(receiver=blocked_user).delete()
        blocked_user.sent_friend_requests.filter(receiver=user).delete()
        validated_data['user'] = user
        validated_data['blocked'] = blocked_user
        return super().create(validated_data)
