from lib_transcendence.exceptions import MessagesException
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from chat_messages.models import Messages
from chat_messages.utils import get_chat_participants
from chats.models import ChatParticipants, Chats


class MessagesSerializer(serializers.ModelSerializer):
    author = serializers.IntegerField(source='author.id', read_only=True)

    class Meta:
        model = Messages
        fields = [
            'id',
            'chat_id',
            'author',
            'content',
            'sent_at',
            'is_read',
        ]
        read_only_fields = [
            'id',
            'author',
            'chat_id',
        ]

    def create(self, validated_data):
        chat_id = self.context['chat_id']
        user_id = self.context['auth_user']['id']

        author = get_chat_participants(chat_id, user_id)

        try:
            chat = Chats.objects.get(id=chat_id)
            chat.update()
        except ChatParticipants.DoesNotExist:
            raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG_TO_CHAT)

        validated_data['chat_id'] = chat_id
        validated_data['author'] = author.user

        for user in chat.participants.filter(view_chat=False):
            user.set_view_chat()

        return super().create(validated_data)
