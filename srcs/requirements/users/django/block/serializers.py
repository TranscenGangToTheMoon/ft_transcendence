from rest_framework import serializers

from block.models import Blocks
from friends.exist import get_friendship
from users.auth import get_user, validate_username


class BlockSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    blocked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Blocks
        fields = '__all__'

    def get_user(self, obj):
        return {'id': obj.user.id, 'username': obj.user.username}

    def get_blocked(self, obj):
        return {'id': obj.blocked.id, 'username': obj.blocked.username}

    def create(self, validated_data):
        user = get_user(self.context.get('request'))

        block_user = validate_username(validated_data.pop('username'), user)

        if block_user == user:
            raise serializers.ValidationError({'username': ['You cannot block yourself.']})

        if user.block.filter(blocked=block_user).exists():
            raise serializers.ValidationError({'username': ['You already block this user.']})

        friendship = get_friendship(user, block_user)
        if friendship:
            friendship.delete()
        user.sent_friend_requests.filter(receiver=block_user).delete()
        block_user.sent_friend_requests.filter(receiver=user).delete()
        validated_data['user'] = user
        validated_data['blocked'] = block_user
        return super().create(validated_data)
