from rest_framework import serializers

from lib_transcendence.game import GameMode
from lobby.models import Lobby
from tournament.models import Tournament


class FinishMatchSerializer(serializers.Serializer):
    game_mode = serializers.CharField(max_length=20)
    tournament_id = serializers.IntegerField(required=False)
    players = serializers.ListSerializer(child=serializers.IntegerField(), required=False)

    def create(self, validated_data):
        if validated_data['game_mode'] == GameMode.TOURNAMENT:
            Tournament.objects.get(id=validated_data['tournament_id']).delete()
        else:
            Lobby.objects.filter(participants__user_id__in=validated_data['players']).distinct().update(game_playing=None)
        return validated_data
