import redis
from rest_framework import serializers

redis_client = redis.StrictRedis(host='redis')


class EventSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    type = serializers.CharField(max_length=10)
    service = serializers.CharField(max_length=10)
    message = serializers.CharField(max_length=100)
    code = serializers.CharField(max_length=5, required=False)

    @staticmethod
    def validate_type(value):
        if value not in ['notification', 'lobby', 'tournament', 'game']:
            raise serializers.ValidationError('Invalid type')
        return value

    @staticmethod
    def validate_service(value):
        if value not in ['messages', 'friends', 'friend_requests', 'invite', 'lobby', 'tournament', 'game']:
            raise serializers.ValidationError('Invalid type')
        return value

    def create(self, validated_data):
        # Publier la notification dans Redis avec user_id
        notification = {
            "service": user_id,
            "message": message
        }
        channel = f' :user_{user_id}'
        try:
            redis_client.publish(channel, json.dumps(notification))
        except redis.exceptions.ConnectionError:
            raise ServiceUnavailable('redis')

        return validated_data
