from rest_framework import serializers

from chat_messages.models import Messages
from chats.models import Chats, ChatParticipants


class MessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ('id', 'chat_id', 'author', 'content', 'sent_at')
        read_only_fields = ('id', 'author', 'chat_id')

    def create(self, validated_data):
        pk = self.context.get('pk')
        if pk is None:
            raise serializers.ValidationError({'detail': 'Chat id is required'})
        if not Chats.objects.filter(pk=pk).exists():
            raise serializers.ValidationError({'chat_id': 'Chat does not exist.'})
        user = self.context['auth_user']
        if not ChatParticipants.objects.filter(chat_id=pk, user_id=user['id']).exists():
            raise serializers.ValidationError({'chat_id': 'You are not participant of this chat'})

        validated_data['chat_id'] = pk
        validated_data['author'] = user['id']
        return super().create(validated_data)
