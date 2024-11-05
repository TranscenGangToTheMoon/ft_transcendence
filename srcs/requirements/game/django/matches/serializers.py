from lib_transcendence.GameMode import GameMode
from lib_transcendence.utils import generate_code
from rest_framework import serializers

from matches.models import Matches, Teams, Players


def validate_user_id(value, return_user=False):
    if type(value) is not int:
        raise serializers.ValidationError(['User id is required.'])

    try:
        player = Players.objects.get(user_id=value, match__finished=False)
        if return_user:
            return player
        raise serializers.ValidationError(['User is already in a match.'])
    except Players.DoesNotExist:
        return None


def validate_team(value):
    if len(value) != 2:
        raise serializers.ValidationError(['Two teams are required.'])
    if len(value[0]) not in (1, 3):
        raise serializers.ValidationError(['Only 1v1 and 3v3 are allowed.'])
    if len(value[0]) != len(value[1]):
        raise serializers.ValidationError(['Both teams must have the same number of players.'])
    for team in value:
        for user in team:
            if type(user) is not int:
                raise serializers.ValidationError(['User id is required.'])
            if Players.objects.filter(user_id=user).exists():
                raise serializers.ValidationError(['User is already in a match.'])
    return value


class MatchSerializer(serializers.ModelSerializer):
    teams = serializers.JSONField(write_only=True, validators=[validate_team])

    class Meta:
        model = Matches
        fields = '__all__'
        read_only_fields = [
            'id',
            'created_at',
        ]

    @staticmethod
    def validate_game_mode(value):
        return GameMode.validate(value)

    def create(self, validated_data):
        if validated_data['game_mode'] == GameMode.tournament:
            if not validated_data.get('tournament_id'):
                raise serializers.ValidationError({'tournament_id': ['Tournament id is required for tournament mode.']})
            if not validated_data.get('tournament_stage_id'):
                raise serializers.ValidationError({'tournament_stage_id': ['Stage tournament id is required for tournament mode.']})
        else:
            validated_data.pop('tournament_id', None)
            validated_data.pop('tournament_stage_id', None)

        validated_data['code'] = generate_code(Matches)
        teams = validated_data.pop('teams')
        if len(teams[0]) == 1 and validated_data['game_mode'] == GameMode.clash:
            raise serializers.ValidationError(['Clash must have 3 players in each teams.'])
        if len(teams[0]) == 3 and (validated_data['game_mode'] != GameMode.clash or validated_data['game_mode'] != GameMode.custom_game):
            raise serializers.ValidationError([f'{validated_data["game_mode"].replace("_", " ").capitalize()} must have 1 player in each team.'])
        if validated_data['game_mode'] != GameMode.tournament:
            validated_data['tournament_id'] = None
            validated_data['tournament_stage_id'] = None
        match = super().create(validated_data)
        for team in teams:
            new_team = Teams.objects.create(match=match)
            for user in team:
                Players.objects.create(user_id=user, match=match, team=new_team)
        return match
