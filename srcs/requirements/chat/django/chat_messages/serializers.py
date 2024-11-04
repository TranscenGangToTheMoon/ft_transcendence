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

        user = self.context['auth_user']
        try:
            chats = Chats.objects.get(pk=pk)

            try:
                participant = chats.participants.get(user_id=user['id'])
                validated_data['chat_id'] = pk
                validated_data['author'] = participant
                return super().create(validated_data)
            except ChatParticipants.DoesNotExist:
                raise serializers.ValidationError({'detail': 'You are not participant of this chat'})
        except Chats.DoesNotExist:
            raise serializers.ValidationError({'detail': 'Chat does not exist.'})
