from lib_transcendence.Chat import ChatType
from lib_transcendence.auth import get_auth_user
from lib_transcendence.services import requests_users
from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed

from chats.models import Chats, ChatParticipants


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
    participants = ChatPaticipantsSerializer(many=True, read_only=True)
    type = serializers.CharField(required=False)
    view_chat = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = Chats
        fields = [
            'id',
            'type',
            'participants',
            'created_at',
            'username',
            'view_chat',
        ]
        read_only_fields = [
            'id',
            'participants',
            'created_at',
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError({'detail': 'Request is required.'}) # todo move in library
        if request.get_host().split(':')[0] == 'chat' and 'type' not in data:
            raise serializers.ValidationError({'type': ['This field is required.']})
        return data

    def validate_type(self, value):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError({'detail': 'Request is required.'})
        if request.method in ('PATCH', 'PUT'):
            raise MethodNotAllowed(request.method)
        ChatType.validate(value)
        if request.get_host().split(':')[0] != 'chat' and value != ChatType.private_message:
            raise serializers.ValidationError('You can only create private messages')
        return value

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

        if request.get_host().split(':')[0] != 'chat':
            validated_data['type'] = 'private_message'
        result = super().create(validated_data)
        ChatParticipants.objects.create(user_id=user['id'], username=user['username'], chat_id=result.id)
        ChatParticipants.objects.create(user_id=user2['id'], username=user2['username'], chat_id=result.id)
        return result

    def update(self, instance, validated_data):
        view_chat = validated_data.pop('view_chat', None)
        if view_chat is not None:
            user = get_auth_user(self.context.get('request'))
            try:
                p = instance.participants.get(user_id=user['id'])
                p.view_chat = view_chat
                p.save()
            except ChatParticipants.DoesNotExist:
                raise serializers.ValidationError({'detail': 'You are not in this chat.'})
        return super().update(instance, validated_data)
