from lib_transcendence import endpoints
from lib_transcendence.auth import get_auth_user
from lib_transcendence.exceptions import MessagesException, ResourceExists
from lib_transcendence.services import request_users
from lib_transcendence.users import retrieve_users
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from chat_messages.serializers import MessagesSerializer
from chats.models import Chats, ChatParticipants
from chats.utils import get_chat_together
from user_management.models import Users


class ChatsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    chat_with = serializers.SerializerMethodField(read_only=True)
    unread_messages = serializers.SerializerMethodField(read_only=True)
    last_message = MessagesSerializer(source='messages.last', read_only=True)

    class Meta:
        model = Chats
        fields = [
            'username',
            'id',
            'chat_with',
            'last_message',
            'created_at',
            'last_updated',
            'unread_messages',
        ]
        read_only_fields = [
            'id',
            'chat_with',
            'last_message',
            'created_at',
            'last_updated',
            'unread_messages',
        ]

    def get_chat_with(self, obj):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError(MessagesException.ValidationError.REQUEST_REQUIRED)
        chat_with = obj.participants.exclude(user__id=get_auth_user(request)['id']).first()
        chat_with_user = retrieve_users(chat_with.user.id)
        return chat_with_user[0]

    def get_unread_messages(self, obj):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError(MessagesException.ValidationError.REQUEST_REQUIRED)
        return obj.messages.exclude(author__id=get_auth_user(request)['id']).filter(is_read=False).count()

    def create(self, validated_data):
        request = self.context.get('request')
        user = get_auth_user(request)

        username = validated_data.pop('username')
        if username == user['username']:
            raise PermissionDenied(MessagesException.PermissionDenied.CANNOT_CHAT_YOURSELF)

        if get_chat_together(user['username'], username):
            raise ResourceExists(MessagesException.ResourceExists.CHAT)

        user2 = request_users(endpoints.Users.fchat.format(user1_id=user['id'], username2=username), 'GET', request)
        result = super().create(validated_data)
        for u in (user, user2):
            user_instance, created = Users.objects.get_or_create(id=u['id'], username=u['username'])
            ChatParticipants.objects.create(user=user_instance, chat_id=result.id)
        return result


class ChatNotificationsSerializer(serializers.Serializer):
    notifications = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_notifications(obj):
        count = 0

        for chat in Chats.objects.filter(participants__user__id=obj):
            if chat.messages.exclude(author__id=obj).filter(is_read=False).exists():
                count += 1

        return count
