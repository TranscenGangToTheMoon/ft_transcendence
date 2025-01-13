from rest_framework import serializers
from lib_transcendence.game import GameMode
from rest_framework.exceptions import APIException

from stats.models import GameModeStats, RankedStats
from users.auth import get_user


class StatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameModeStats
        fields = [
            'game_mode',
            'scored',
            'game_played',
            'wins',
            'longest_win_streak',
            'current_win_streak',
            'tournament_wins',
            'own_goals',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not GameMode.tournament_field(instance.game_mode):
            representation.pop('tournament_wins')
        if not GameMode.own_goal_field(instance.game_mode):
            representation.pop('own_goals')
        return representation


class RankedStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RankedStats
        fields = '__all__'


class UserFinishMatchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    score = serializers.IntegerField()
    own_goals = serializers.IntegerField(required=False)
    trophies = serializers.IntegerField(required=False)


class TeamsFinishMatchSerializer(serializers.Serializer):
    a = UserFinishMatchSerializer(many=True)
    b = UserFinishMatchSerializer(many=True)


class FinishMatchSerializer(serializers.Serializer):
    game_mode = serializers.CharField(max_length=20)
    winner = serializers.CharField(max_length=1)
    looser = serializers.CharField(max_length=1)
    score_winner = serializers.IntegerField()
    score_looser = serializers.IntegerField()
    teams = TeamsFinishMatchSerializer()

    @staticmethod
    def validate_game_mode(value):
        return GameMode.validate(value)

    def create(self, validated_data):
        for team_name, team_users in validated_data['teams'].items():
            for user_json in team_users:
                try:
                    if validated_data['game_mode'] == GameMode.CLASH and 'own_goals' in user_json:
                        own_goals = validated_data['own_goals']
                    else:
                        own_goals = None
                    user = get_user(id=user_json['id'])
                    user.set_game_playing()
                    stat = user.stats.get(game_mode=validated_data['game_mode'])
                    stat.log(user_json['score'], team_name == validated_data['winner'], own_goals)
                    if validated_data['game_mode'] == GameMode.RANKED and 'trophies' in user_json:
                        RankedStats.log(user, user_json['trophies'])
                except APIException:
                    pass
        return validated_data


class FinishTournamentSerializer(serializers.Serializer):
    winner = serializers.IntegerField()

    def create(self, validated_data):
        winner = get_user(id=validated_data['winner'])
        winner.stats.get(game_mode=GameMode.TOURNAMENT).win_tournament()
        return validated_data
