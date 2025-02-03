from rest_framework import serializers
from rest_framework.exceptions import NotFound

from lib_transcendence.exceptions import MessagesException
from lib_transcendence.sse_events import EventCode
from sse.events import publish_event
from users.auth import get_user


class EventSerializer(serializers.Serializer):
    users_id = serializers.ListField(child=serializers.IntegerField())
    event_code = serializers.CharField(max_length=50)
    data = serializers.DictField(required=False)
    kwargs = serializers.DictField(required=False)

    @staticmethod
    def validate_users_id(value):
        result = list(set(value))
        if not result:
            raise NotFound(MessagesException.NotFound.USERS)
        return result

    @staticmethod
    def validate_event_code(value):
        if value not in EventCode.attr():
            raise serializers.ValidationError(MessagesException.ValidationError.INVALID_EVENT_CODE)
        return value

    def create(self, validated_data):
        one_user = len(validated_data['users_id']) == 1
        users_id = []
        for user_id in validated_data['users_id']:
            user = get_user(id=user_id)
            if not user.is_online and one_user:
                raise NotFound(MessagesException.NotFound.USER)
            users_id.append(user)
        publish_event(users_id, validated_data['event_code'], validated_data.get('data'), validated_data.get('kwargs'))
        return validated_data
