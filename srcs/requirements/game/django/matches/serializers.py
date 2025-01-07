from lib_transcendence.game import GameMode, Reason
from lib_transcendence.generate import generate_code
from lib_transcendence.exceptions import MessagesException, Conflict, ResourceExists
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
    teams = serializers.JSONField(validators=[validate_teams])
    score_winner = serializers.IntegerField(read_only=True)
    score_looser = serializers.IntegerField(read_only=True)

    class Meta:
        model = Matches
        fields = [
            'id',
            'code',
            'game_mode',
            'created_at',
            'game_duration',
            'finished',
            'tournament_id',
            'tournament_stage_id',
            'teams',
            'winner',
            'looser',
            'score_winner',
            'score_looser',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'winner',
            'looser',
            'score_winner',
            'score_looser',
        ]
        ]

    @staticmethod
    def validate_game_mode(value):
        return GameMode.validate(value)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        users = retrieve_users(list(instance.players.all().values_list('user_id', flat=True)))
        teams = {}
        for name in Teams.names:
            teams[name] = []
        for user in users:
            player = instance.players.get(user_id=user['id'])
            teams[player.team.name].append({**user, 'score': player.score})
        representation['teams'] = teams
        if instance.finished:
            representation.pop('code')
            representation['winner'] = instance.winner.name
            representation['looser'] = instance.looser.name
            representation['score_winner'] = instance.winner.score
            representation['score_looser'] = instance.looser.score
        if representation['tournament_id'] is None:
            representation.pop('tournament_id')
        return representation

    def create(self, validated_data):
        if validated_data['game_mode'] == GameMode.tournament:
            if not validated_data.get('tournament_id'):
                raise serializers.ValidationError({'tournament_id': [MessagesException.ValidationError.FIELD_REQUIRED]})
            if not validated_data.get('tournament_stage_id'):
                raise serializers.ValidationError({'tournament_stage_id': [MessagesException.ValidationError.FIELD_REQUIRED]})
        else:
            validated_data.pop('tournament_id', None)

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
        for n, team in enumerate(teams):
            new_team = Teams.objects.create(match=match, name=Teams.names[n])
            for user in team:
                Players.objects.create(user_id=user, match=match, team=new_team)
        return match


class MatchFinishSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, write_only=True)
    reason = serializers.CharField(required=True)

    class Meta:
        model = Matches
        fields = [
            'id',
            'user_id',
            'reason',
            'finished',
        ]
        read_only_fields = [
            'id',
        ]

    @staticmethod
    def validate_reason(value):
        return Reason.validate_error(value)

    def update(self, instance, validated_data):
        if instance.finished:
            raise ResourceExists(MessagesException.ResourceExists.MATCH)
        user_id = validated_data.pop('user_id')
        try:
            player = instance.players.get(user_id=user_id)
        except Players.DoesNotExist:
            raise NotFound(MessagesException.NotFound.NOT_BELONG_MATCH)
        player.team.score = 0
        player.save()
        winner = instance.players.exclude(user_id=player.user_id).first()
        winner.team.score = 3
        winner.save()
        validated_data['finished'] = True
        result = super().update(instance, validated_data)
        result.finish_match()
        return result
