import json

import redis
from lib_transcendence.exceptions import MessagesException, ServiceUnavailable
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from users.auth import get_user

redis_client = redis.StrictRedis(host='redis')


class SSEType:
    notification = 'notification'
    event = 'event'


events = {
    'chat':
        {
            'send-message': {'type': SSEType.notification, 'db_field': 'chat_notifications', 'message': '{username}: {message}', 'target': 'open chat with user sending message', 'requiere-data': ['message_instance (user instance send, chat id, message']},
        },
    'friends':
        {
            'accept-friend-requests': {'type': SSEType.notification, 'db_field': None, 'message': '{username} has accepted your friend request!', 'target': 'open friend profile (not usefull)', 'required-data': ['friend instance (friencd accpeting, friend receive, profile user instance accepting']},
            'receive-friend-requests': {'type': SSEType.notification, 'db_field': 'friend_notifications', 'message': '{username} want to become friend with you, accept ? warning peolple can be weird', 'target': 'v (for accepting) x (for rejecting) o (for blocking)', 'required-data': ['friend request instance (friend sending, friend receive, profile user instance sending']},
            'update-status': {'type': SSEType.event, 'db_field': None, 'message': None, 'target': 'update status user view', 'required-data': ['user_id', 'new status']}, # todo handle update status
        },
    'invite':
        {
            'invite-game': {'type': SSEType.notification, 'db_field': 'friend_notifications', 'message': '{username} challeging you to an epic battle, do you accept the challenge?', 'target': 'v (for accpeting challenge) x (for decline invitation)', 'required-data': ['user inviting instance', 'lobby code']},
            'invite-clash': {'type': SSEType.notification, 'db_field': None, 'message': '{username} inviting you to play clash, a 3v3 fun game !', 'target': 'v (for joinning clash) x (for decline invitation)', 'required-data': ['user inviting instance', 'lobby code']},
            'invite-custom-game': {'type': SSEType.notification, 'db_field': None, 'message': '{username} inviting you to play custom game !', 'target': 'v (for joinning custum game) x (for decline invitation)', 'required-data': ['user inviting instance', 'lobby code']},
            'invite-tournament': {'type': SSEType.notification, 'db_field': None, 'message': '{username} inviting you to play tournament {tournament.name} !', 'target': 'v (for joinning tournament) x (for decline invitation)', 'required-data': ['user inviting instance', 'lobby code']},
        },
    'lobby':
        {
            'join-lobby': {'type': SSEType.event, 'db_field': None, 'message': '{username} join the lobby', 'target': 'add user view', 'required-data': ['user instance joinning lobby']},
            'leave-lobby': {'type': SSEType.event, 'db_field': None, 'message': '{username} leave the lobby', 'target': 'remove user view', 'required-data': ['user instance leaving lobby']},
            'set-ready-lobby': {'type': SSEType.event, 'db_field': None, 'message': '{username} is ready to fight (useless ?)', 'target': 'update view and if all user are ready change view (replace it by searching view)', 'required-data': ['user instance set ready lobby']},
        },
    'game':
        {
            'game-start': {'type': SSEType.event, 'db_field': None, 'message': '', 'target': 'connect to web socket and move players to game', 'required-data': ['game instance (teams, users id, profile, etcc)']},
        },
    'tournament': # todo make
        {
            'tournament-start-3': {'type': SSEType.event, 'db_field': None, 'message': '', 'target': None, 'required-data': []},
            'tournament-start-27': {'type': SSEType.event, 'db_field': None, 'message': '', 'target': None, 'required-data': []},
            'tournament-start-cancel': {'type': SSEType.event, 'db_field': None, 'message': '', 'target': None, 'required-data': []},
            'tournament-match-end': {'type': SSEType.event, 'db_field': None, 'message': '', 'target': None, 'required-data': []},
        },
}


class EventSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    type = serializers.CharField(max_length=20)
    service = serializers.CharField(max_length=20)
    event_code = serializers.CharField(max_length=20)
    data = serializers.DictField(required=False)

    @staticmethod
    def validate_service(value):
        if value not in events.keys():
            raise serializers.ValidationError('Invalid service') # todo add message to lib
        return value

    @staticmethod
    def validate_type(value):
        if value not in (SSEType.event, SSEType.notification):
            raise serializers.ValidationError('Invalid sse type') # todo add message to lib
        return value

    def validate_event_code(self, value):
        if value not in events[self.initial_data['service']]:
            raise serializers.ValidationError('Invalid event code') # todo add message to lib
        return value

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        if not get_user(id=user_id).is_online:
            raise NotFound(MessagesException.NotFound.USER)
        channel = f'events:user_{user_id}'

        try:
            redis_client.publish(channel, json.dumps(validated_data))
        except redis.exceptions.ConnectionError:
            raise ServiceUnavailable('redis')

        return validated_data
