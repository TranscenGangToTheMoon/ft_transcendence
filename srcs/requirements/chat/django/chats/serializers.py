from rest_framework import serializers

from chat.auth import get_auth_user, validate_username
from chat.type import chat_type
from chats.models import Chats, ChatParticipants


class ChatsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    participants = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Chats
        fields = '__all__'

    def validate_type(self, value):
        if value not in chat_type:
            raise serializers.ValidationError('Invalid type')
        return value

    def get_participants(self, obj):
        participants = []
        for user in ChatParticipants.objects.filter(chat=obj.id):
            participants.append({'id': user.user_id, 'username': 'RANDOM_USERNAME'})
        return participants

    def create(self, validated_data):
        request = self.context.get('request')
        user = get_auth_user(request)

        username = validated_data.pop('username')
        if username == user['username']:
            raise serializers.ValidationError({'username': ["You can't chat with yourself."]})

        if ChatParticipants.objects.filter(username=user['username']).filter(username=username).exists():
            raise serializers.ValidationError({'username': ['You are already chat with this user.']})

        user2 = validate_username(request, username)

        result = super().create(validated_data)
        ChatParticipants.objects.create(user_id=user['id'], chat_id=result.id)
        ChatParticipants.objects.create(user_id=user2['id'], chat_id=result.id)
        return result
