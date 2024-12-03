from lib_transcendence.game import GameMode
from lib_transcendence.auth import get_auth_user
from lib_transcendence.exceptions import MessagesException
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from matchmaking.utils import verify_user
from play.models import Players

import threading

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

        if user['is_guest'] and validated_data.get('game_mode') == GameMode.ranked:
            raise PermissionDenied(MessagesException.PermissionDenied.GUEST_CANNOT_PLAY_RANKED)

        validated_data['user_id'] = user['id']
        validated_data['trophies'] = user['trophies']
        # threading.Thread(target=func).start()
        return super().create(validated_data)

# def func():
# 	import subprocess
# 	import time
# 	time.sleep(10)
# 	subprocess.run(["python", "matchmaking/matchmaking.py"])
