from rest_framework import serializers

from chat_messages.models import Messages
from chat_messages.utils import get_chat_participants
from chats.models import ChatParticipants


class MessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = [
            'id',
            'chat_id',
            'author',
            'content',
            'sent_at'
        ]
        read_only_fields = [
            'id',
            'author',
            'chat_id'
        ]

    def create(self, validated_data):
        # todo add check: only chat can creat chat
        chat_id = self.context['chat_id']

        validated_data['chat_id'] = chat_id
        validated_data['author'] = get_chat_participants(chat_id, self.context['auth_user']['id'])

        for user in ChatParticipants.objects.filter(chat_id=chat_id, view_chat=False):
            user.set_view_chat()

        return super().create(validated_data)
