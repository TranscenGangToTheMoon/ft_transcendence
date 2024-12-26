from lib_transcendence.game import GameMode
from lib_transcendence.auth import get_auth_user
from lib_transcendence.exceptions import MessagesException
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from blocking.utils import create_player_instance
from matchmaking.utils import verify_user
from play.models import Players


class PlayersSerializer(serializers.ModelSerializer):
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
        request = self.context.get('request')
        user = get_auth_user(request)

        verify_user(user['id'])

        if user['is_guest'] and validated_data.get('game_mode') == GameMode.ranked:
            raise PermissionDenied(MessagesException.PermissionDenied.GUEST_CANNOT_PLAY_RANKED)

        validated_data['user_id'] = user['id']
        validated_data['trophies'] = user['trophies']
        return create_player_instance(request, Players, **validated_data)
