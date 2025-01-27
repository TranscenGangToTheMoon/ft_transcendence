from rest_framework import serializers
from lib_transcendence.game import GameMode
from rest_framework.exceptions import APIException
from lib_transcendence.serializer import Serializer
from profile_pictures.unlock import unlock_tournament_pp, unlock_duel_clash_pp, unlock_game_played_pp, \
    unlock_scorer_pp, unlock_winning_streak_pp

from stats.models import GameModeStats, RankedStats
from users.auth import get_user


class StatsSerializer(Serializer):
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


class RankedStatsSerializer(Serializer):
    class Meta:
        model = RankedStats
        fields = '__all__'


class UserFinishMatchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    score = serializers.IntegerField()
    own_goals = serializers.IntegerField(required=False)
    trophies = serializers.IntegerField(required=False)


class TeamFinishMatchSerializer(serializers.Serializer):
    score = serializers.IntegerField()
    players = UserFinishMatchSerializer(many=True)


class TeamsFinishMatchSerializer(serializers.Serializer):
    a = TeamFinishMatchSerializer()
    b = TeamFinishMatchSerializer()


class FinishMatchSerializer(serializers.Serializer):
    game_mode = serializers.CharField(max_length=20)
    winner = serializers.CharField(max_length=1)
    looser = serializers.CharField(max_length=1)
    teams = TeamsFinishMatchSerializer()

    @staticmethod
    def validate_game_mode(value):
        return GameMode.validate(value)

    def create(self, validated_data):
        for team_name, team_users in validated_data['teams'].items():
            for user_json in team_users['players']:
                try:
                    user = get_user(id=user_json['id'])
                except APIException:
                    continue
                user.set_game_playing()
                if validated_data['game_mode'] != GameMode.CUSTOM_GAME:
                    if validated_data['game_mode'] == GameMode.CLASH and 'own_goals' in user_json:
                        own_goals = validated_data['own_goals']
                    else:
                        own_goals = None
                    stat = user.stats.get(game_mode=validated_data['game_mode'])
                    stat.log(user_json['score'], team_name == validated_data['winner'], own_goals)
                    unlock_winning_streak_pp(user, stat)
                    if validated_data['game_mode'] in (GameMode.DUEL, GameMode.CLASH):
                        unlock_duel_clash_pp(user, stat, validated_data['game_mode'])
                    if validated_data['game_mode'] == GameMode.RANKED and 'trophies' in user_json:
                        RankedStats.log(user, user_json['trophies'])
                    unlock_game_played_pp(user)
                    unlock_scorer_pp(user)

        return validated_data


class FinishTournamentSerializer(serializers.Serializer):
    winner = serializers.IntegerField()

    def create(self, validated_data):
        winner = get_user(id=validated_data['winner'])
        winner.stats.get(game_mode=GameMode.TOURNAMENT).win_tournament()
        unlock_tournament_pp(winner)
        return validated_data
