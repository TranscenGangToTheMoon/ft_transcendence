from lib_transcendence.exceptions import MessagesException
from rest_framework import serializers
from rest_framework.exceptions import NotFound, APIException

from sse.events import events, publish_event
from users.auth import get_user


class EventSerializer(serializers.Serializer):
    users_id = serializers.ListField(child=serializers.IntegerField())
    service = serializers.CharField(max_length=20)
    event_code = serializers.CharField(max_length=30)
    data = serializers.DictField(required=False)

    @staticmethod
    def validate_users_id(value):
        result = []
        users = set(value)
        for user_id in users:
            try:
                if get_user(id=user_id).is_online:
                    result.append(user_id)
            except APIException:
                pass

        if not result:
            raise NotFound(MessagesException.NotFound.USERS)
        return result

    @staticmethod
    def validate_service(value):
        if value not in events.keys():
            raise serializers.ValidationError(MessagesException.ValidationError.INVALID_SERVICE)
        return value

    def validate_event_code(self, value):
        service = self.initial_data.get('service')
        self.validate_service(service)
        if value not in events[service]:
            raise serializers.ValidationError(MessagesException.ValidationError.INVALID_EVENT_CODE)
        return value

    def create(self, validated_data):
        for user_id in validated_data['users_id']:
            if not get_user(id=user_id).is_online:
                raise NotFound(MessagesException.NotFound.USER)
            publish_event(user_id, validated_data['service'], validated_data['event_code'], validated_data.get('data'))

        return validated_data
