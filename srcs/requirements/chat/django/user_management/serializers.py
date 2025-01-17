from rest_framework import serializers
from lib_transcendence.serializer import Serializer

from chat_messages.serializers import MessagesSerializer
from chats.models import Chats
from user_management.models import Users


class UserDataSerializer(Serializer):
    chat_with = serializers.SerializerMethodField(read_only=True)
    messages = MessagesSerializer(read_only=True, many=True)
    view_chat = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Chats
        fields = [
            'id',
            'chat_with',
            'blocked',
            'view_chat',
            'last_updated',
            'created_at',
            'messages',
        ]

    def get_chat_with(self, obj):
        chat_with = obj.participants.exclude(user__id=self.context['user_id']).first()
        return {'id': chat_with.user.id, 'username': chat_with.user.username}

    def get_view_chat(self, obj):
        return obj.participants.get(user__id=self.context['user_id']).view_chat


class UserSerializer(Serializer):
    class Meta:
        model = Users
        fields = [
            'username',
        ]


class BlockChatSerializer(Serializer):
    class Meta:
        model = Chats
        fields = [
            'id',
            'blocked',
        ]
        read_only_fields = [
            'id',
        ]
