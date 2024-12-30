from lib_transcendence.game import GameMode
from lib_transcendence.generate import generate_code
from lib_transcendence.exceptions import MessagesException, Conflict
from lib_transcendence.users import retrieve_users
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from matches.models import Matches, Teams, Players


def validate_user_id(value, return_user=False):
    if type(value) is not int:
        raise serializers.ValidationError(MessagesException.ValidationError.USER_ID_REQUIRED)

    try:
        player = Players.objects.get(user_id=value, match__finished=False)
        if return_user:
            return player.match
        raise Conflict(MessagesException.Conflict.USER_ALREADY_IN_GAME)
    except Players.DoesNotExist:
        if return_user:
            raise NotFound(MessagesException.NotFound.NOT_BELONG_GAME)


def validate_teams(value):
    if type(value) is not list or type(value[0]) is not list or type(value[1]) is not list:
        raise serializers.ValidationError(MessagesException.ValidationError.TEAMS_LIST)
    if len(value) != 2:
        raise serializers.ValidationError(MessagesException.ValidationError.TEAM_REQUIRED)
    if len(value[0]) not in (1, 3):
        raise serializers.ValidationError(MessagesException.ValidationError.ONLY_1V1_3V3_ALLOWED)
    if len(value[0]) != len(value[1]):
        raise serializers.ValidationError(MessagesException.ValidationError.TEAMS_NOT_EQUAL)
    for team in value:
        for user in team:
            validate_user_id(user)
    for user in value[0]:
        if user in value[1]:
            raise serializers.ValidationError(MessagesException.ValidationError.IN_BOTH_TEAMS)
    return value


class MatchSerializer(serializers.ModelSerializer):
    teams = serializers.JSONField(write_only=True, validators=[validate_teams])
    team_a = serializers.SerializerMethodField(read_only=True)
    team_b = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Matches
        fields = '__all__'
        read_only_fields = [
            'id',
            'created_at',
            'team_a',
            'team_b',
        ]

    @staticmethod
    def validate_game_mode(value):
        return GameMode.validate(value)

    def get_team_a(self, value):
        return retrieve_users(self.validated_data['teams'][0])

    def get_team_b(self, value):
        return retrieve_users(self.validated_data['teams'][1])

    def create(self, validated_data):
        if validated_data['game_mode'] == GameMode.tournament:
            if not validated_data.get('tournament_id'):
                raise serializers.ValidationError({'tournament_id': [MessagesException.ValidationError.TOURNAMENT_ID_REQUIRED]})
            if not validated_data.get('tournament_stage_id'):
                raise serializers.ValidationError({'tournament_stage_id': [MessagesException.ValidationError.TOURNAMENT_STAGE_ID_REQUIRED]})
        else:
            validated_data.pop('tournament_id', None)
            validated_data.pop('tournament_stage_id', None)

        validated_data['code'] = generate_code(Matches)
        teams = validated_data.pop('teams')
        if len(teams[0]) == 1 and validated_data['game_mode'] == GameMode.clash:
            raise serializers.ValidationError(MessagesException.ValidationError.CLASH_3_PLAYERS)
        if len(teams[0]) == 3 and (validated_data['game_mode'] != GameMode.clash or validated_data['game_mode'] != GameMode.custom_game):
            raise serializers.ValidationError(MessagesException.ValidationError.GAME_MODE_PLAYERS.format(obj=validated_data['game_mode'].replace('_', ' ').capitalize(), n=1))
        if validated_data['game_mode'] != GameMode.tournament:
            validated_data['tournament_id'] = None
            validated_data['tournament_stage_id'] = None
        match = super().create(validated_data)
        for team in teams:
            new_team = Teams.objects.create(match=match)
            for user in team:
                Players.objects.create(user_id=user, match=match, team=new_team)
        return match
