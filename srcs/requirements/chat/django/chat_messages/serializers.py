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
        pk = self.context['pk']
        user = self.context['auth_user']

        try:
            participant = ChatParticipants.objects.get(user_id=user['id'], chat_id=pk)
        except ChatParticipants.DoesNotExist:
            raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG_TO_CHAT)
        validated_data['author'] = get_chat_participants(chat_id, self.context['auth_user']['id'])

        validated_data['chat_id'] = pk
        return super().create(validated_data)
