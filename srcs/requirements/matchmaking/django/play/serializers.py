from lib_transcendence.auth import get_auth_user
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

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
        user = get_auth_user(self.context.get('request'))

        verify_user(user['id'])

        if user['is_guest'] and validated_data.get('game_mode') == 'ranked':
            raise PermissionDenied('Guest cannot play ranked game.')

        validated_data['user_id'] = user['id']
        validated_data['trophies'] = user['trophies']
        return super().create(validated_data)
        # todo block user can't play together
