from rest_framework import serializers

from chat.auth import get_auth_user, requests_users
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
            raise serializers.ValidationError('Invalid type, only accept "' + '", "'.join(chat_type) + '"')
        return value

    def get_participants(self, obj):
        participants = []
        for user in obj.chatparticipants_set.all():
            participants.append({'id': user.user_id, 'username': user.username})
        return participants

    def create(self, validated_data):
        request = self.context.get('request')
        user = get_auth_user(request)

        username = validated_data.pop('username')
        if username == user['username']:
            raise serializers.ValidationError({'username': ["You can't chat with yourself."]})

        user_1_chats = ChatParticipants.objects.filter(username=user['username']).values_list('chat_id', flat=True)
        user_2_chats = ChatParticipants.objects.filter(username=username).values_list('chat_id', flat=True)
        if set(user_1_chats).intersection(set(user_2_chats)):
            raise serializers.ValidationError({'username': ['You are already chat with this user.']})

        user2 = requests_users(request, 'validate/chat/', 'GET', data={'username': username})

        result = super().create(validated_data)
        ChatParticipants.objects.create(user_id=user['id'], username=user['username'], chat_id=result.id)
        ChatParticipants.objects.create(user_id=user2['id'], username=user2['username'], chat_id=result.id)
        return result
