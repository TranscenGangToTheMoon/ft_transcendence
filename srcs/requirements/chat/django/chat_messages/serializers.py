from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from lib_transcendence.exceptions import MessagesException

from chat_messages.models import Messages
from chats.models import Chats, ChatParticipants


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

    def create(self, validated_data): # todo useless, delete ?
        pk = self.context.get('pk')
        if pk is None:
            raise serializers.ValidationError('Chat id is required')

        user = self.context['auth_user']
        try:
            chats = Chats.objects.get(pk=pk)
        except Chats.DoesNotExist:
            raise serializers.ValidationError('Chat does not exist.')

        try:
            participant = chats.participants.get(user_id=user['id'])
        except ChatParticipants.DoesNotExist:
            raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG_TO_CHAT)

        validated_data['chat_id'] = pk
        validated_data['author'] = participant
        return super().create(validated_data)
