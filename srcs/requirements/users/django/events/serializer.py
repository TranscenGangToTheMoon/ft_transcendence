import json

import redis
from lib_transcendence.exceptions import MessagesException, ServiceUnavailable
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from users.auth import get_user

redis_client = redis.StrictRedis(host='redis')


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
