from rest_framework import serializers

from matchmaking.sse import send_sse_event


class MessageSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField(read_only=True)
    content = serializers.CharField()

    @staticmethod
    def validate_content(value):
        return value.strip()

    def get_id(self, _):
        return self.context['auth_user']['id']

    def create(self, validated_data):
        place = self.context['place'](code=self.context['code'])
        participant = self.context['participant'](place, self.context['auth_user']['id'])
        send_sse_event(self.context['event_code'], participant, validated_data.copy())
        return validated_data
