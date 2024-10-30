from lib-transcendence.auth import get_auth_user
from rest_framework import serializers

from matchmaking.utils import verify_user
from play.models import Players


class PlayersSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user_id', read_only=True)

    class Meta:
        model = Players
        fields = [
            'id',
            'game_mode',
            'join_at',
        ]

    def create(self, validated_data):
        user = get_auth_user(self.context.get('request'))

        verify_user(user['id'])

        if user['is_guest'] and validated_data.get('game_mode') == 'ranked':
            raise serializers.ValidationError({'detail': 'Guest cannot play ranked game.'})

        validated_data['user_id'] = user['id']
        return super().create(validated_data)
