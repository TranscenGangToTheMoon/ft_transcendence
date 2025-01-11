from rest_framework import serializers

from chats.models import Chats
from user_management.models import Users


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            'username',
        ]


class BlockChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chats
        fields = [
            'id',
            'blocked',
        ]
        read_only_fields = [
            'id',
        ]
