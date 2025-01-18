from rest_framework import serializers

from matchmaking.utils.sse import send_sse_event


class MessageSerializer(serializers.Serializer):
    content = serializers.CharField()

    @staticmethod
    def validate_content(value):
        return value.strip()

    def create(self, validated_data):
        place = self.context['place'](code=self.context['code'])
        participant = self.context['participant'](place, self.context['auth_user']['id'])
        send_sse_event(self.context['event_code'], participant, validated_data.copy())
        return validated_data
