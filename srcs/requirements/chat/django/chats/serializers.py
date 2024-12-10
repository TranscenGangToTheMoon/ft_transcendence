from lib_transcendence import endpoints
from lib_transcendence.Chat import ChatType
from lib_transcendence.auth import get_auth_user
from lib_transcendence.services import request_users
from lib_transcendence.utils import get_host
from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.exceptions import ResourceExists

from chat_messages.serializers import MessagesSerializer
from chats.models import Chats, ChatParticipants
from chats.utils import get_chat_together


class ChatPaticipantsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user_id', read_only=True)

    class Meta:
        model = ChatParticipants
        fields = [
            'id',
            'username',
            'view_chat',
        ]


class ChatsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    chat_with = serializers.SerializerMethodField(read_only=True)
    last_message = MessagesSerializer(source='messages.last', read_only=True)
    type = serializers.CharField()
    view_chat = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = Chats
        fields = [
            'id',
            'type',
            'chat_with',
            'last_message',
            'created_at',
            'username',
            'view_chat',
        ]
        read_only_fields = [
            'id',
            'chat_with',
            'last_message',
            'created_at',
        ]

    def get_chat_with(self, obj):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError(MessagesException.ValidationError.REQUEST_REQUIRED)
        chat_with = obj.participants.exclude(user_id=get_auth_user(request)['id']).first()
        return {'id': chat_with.user_id, 'username': chat_with.username}

    def validate_type(self, value):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError(MessagesException.ValidationError.REQUEST_REQUIRED)
        ChatType.validate(value)
        if get_host(request) != 'chat' and value != ChatType.private_message:
            raise PermissionDenied(MessagesException.PermissionDenied.ONLY_CREATE_PRIVATE_MESSAGES)
        if request.method in ('PATCH', 'PUT'):
            raise MethodNotAllowed(request.method)
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        user = get_auth_user(request)

        if user['is_guest']:
            raise PermissionDenied(MessagesException.PermissionDenied.GUEST_CREATE_CHAT)

        username = validated_data.pop('username')
        if username == user['username']:
            raise PermissionDenied(MessagesException.PermissionDenied.CANNOT_CHAT_YOURSELF)

        if get_chat_together(user['username'], username):
            raise ResourceExists(MessagesException.ResourceExists.CHAT)

        user2 = request_users(endpoints.Users.fchat.format(user1_id=user['id'], username2=username), 'GET', request)

        if get_host(request) != 'chat':
            validated_data['type'] = 'private_message'
        result = super().create(validated_data)
        ChatParticipants.objects.create(user_id=user['id'], username=user['username'], chat_id=result.id)
        ChatParticipants.objects.create(user_id=user2['id'], username=user2['username'], chat_id=result.id)
        return result


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
