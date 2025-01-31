from rest_framework import serializers

from blocking.utils import create_player_instance
from lib_transcendence.auth import get_auth_user
from lib_transcendence.serializer import Serializer
from matchmaking.utils.user import verify_user
from play.models import Players


class PlayersSerializer(Serializer):
    id = serializers.IntegerField(source='user_id', read_only=True)

    class Meta:
        model = Players
        fields = [
            'id',
            'game_mode',
            'trophies',
            'join_at',
        ]
        read_only_fields = [
            'id',
            'trophies',
            'join_at',
        ]

    def create(self, validated_data):
        user = get_auth_user(self.context.get('request'))

        verify_user(user['id'])

        validated_data['user_id'] = user['id']
        validated_data['trophies'] = user['trophies']
        return create_player_instance(user, Players, **validated_data)
