from rest_framework import serializers

from game.auth import generate_game_code
from game.static import GameMode
from matches.models import Matches


class MatchSerializer(serializers.Serializer):

    class Meta:
        model = Matches
        fields = '__all__'
        read_only_fields = [
            'id',
            'created_at',
        ]

    def validate_game_mode(self, value):
        if value not in GameMode.all():
            raise serializers.ValidationError([f"Game mode must be {GameMode}."])
        return value

    def create(self, validated_data):
        validated_data['code'] = generate_game_code()
        return super().create(validated_data)
