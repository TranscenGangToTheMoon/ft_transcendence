import os

from lib_transcendence.game import GameMode, FinishReason
from lib_transcendence.generate import generate_code
from lib_transcendence.exceptions import MessagesException, Conflict, ResourceExists
from lib_transcendence.lobby import MatchType
from lib_transcendence.users import retrieve_users
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied
from lib_transcendence.serializer import Serializer

from matches.models import Matches, Teams, Players


def validate_user_id(value, return_match=False, kwargs=None):
    if kwargs is None:
        kwargs = {}
    try:
        player = Players.objects.get(user_id=value, match__finished=False, **kwargs)
        if return_match:
            return player.match
        raise Conflict(MessagesException.Conflict.USER_ALREADY_IN_GAME)
    except Players.DoesNotExist:
        if return_match:
            if kwargs:
                return PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG_GAME)
            raise NotFound(MessagesException.NotFound.NOT_BELONG_GAME)


class TeamsSerializer(serializers.Serializer):
    a = serializers.ListSerializer(child=serializers.IntegerField(validators=[validate_user_id]))
    b = serializers.ListSerializer(child=serializers.IntegerField(validators=[validate_user_id]))

    def validate(self, attrs):
        attr = super().validate(attrs)
        if len(attr['a']) != len(attr['b']):
            raise serializers.ValidationError(MessagesException.ValidationError.TEAMS_NOT_EQUAL)
        if len(attr['a']) not in (1, 3):
            raise serializers.ValidationError(MessagesException.ValidationError.ONLY_1V1_3V3_ALLOWED)
        if len(attr['a'] + attr['b']) != len(set(attr['a'] + attr['b'])):
            raise serializers.ValidationError(MessagesException.ValidationError.IN_BOTH_TEAMS)
        return attr


class MatchSerializer(Serializer):
    teams = TeamsSerializer(write_only=True)

    class Meta:
        model = Matches
        fields = [
            'id',
            'code',
            'game_mode',
            'created_at',
            'game_duration',
            'tournament_id',
            'tournament_stage_id',
            'tournament_n',
            'match_type',
            'finished',
            'teams',
            'winner',
            'looser',
        ]
        read_only_fields = [
            'id',
            'match_type',
            'finished',
            'created_at',
            'winner',
            'looser',
        ]
        write_only_fields = [
            'game_mode'
            'tournament_id'
            'tournament_stage_id'
            'tournament_n'
            'teams'
        ]

    @staticmethod
    def validate_game_mode(value):
        return GameMode.validate(value)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('retrieve_users', True):
            users = retrieve_users(list(instance.players.all().values_list('user_id', flat=True)), return_type=dict)
        else:
            users = {}
        teams = {}
        for team in ('a', 'b'):
            teams[team] = {'score': instance.teams.get(name=team).score, 'players': []}
            for player in instance.teams.get(name=team).players.all():
                add_user = users.get(player.user_id)
                if add_user is None:
                    add_user = {'id': player.user_id}
                if instance.game_mode == GameMode.RANKED:
                    add_user['trophies'] = player.trophies
                if instance.game_mode == GameMode.CLASH:
                    add_user['own_goal'] = player.own_goal
                teams[team]['players'].append({**add_user, 'score': player.score})
        representation['teams'] = teams
        if instance.finished:
            representation.pop('code')
            representation['winner'] = instance.winner.name
            representation['looser'] = instance.looser.name
        if representation['tournament_id'] is None:
            representation.pop('tournament_id')
        return representation

    def create(self, validated_data):
        if validated_data['game_mode'] == GameMode.TOURNAMENT:
            if not validated_data.get('tournament_id'):
                raise serializers.ValidationError({'tournament_id': [MessagesException.ValidationError.FIELD_REQUIRED]})
            if not validated_data.get('tournament_stage_id'):
                raise serializers.ValidationError({'tournament_stage_id': [MessagesException.ValidationError.FIELD_REQUIRED]})
            if not validated_data.get('tournament_n'):
                raise serializers.ValidationError({'tournament_n': [MessagesException.ValidationError.FIELD_REQUIRED]})
        else:
            validated_data.pop('tournament_id', None)
            validated_data.pop('tournament_stage_id', None)
            validated_data.pop('tournament_n', None)

        validated_data['code'] = generate_code(Matches)
        teams = validated_data.pop('teams')
        if len(teams['a']) == 1 and validated_data['game_mode'] == GameMode.CLASH:
            raise serializers.ValidationError(MessagesException.ValidationError.CLASH_3_PLAYERS)
        if len(teams['b']) == 3 and validated_data['game_mode'] not in (GameMode.CLASH, GameMode.CUSTOM_GAME):
            raise serializers.ValidationError(MessagesException.ValidationError.GAME_MODE_PLAYERS.format(obj=validated_data['game_mode'].replace('_', ' ').capitalize(), n=1))

        if len(teams['a']) == 1:
            validated_data['match_type'] = MatchType.M1V1
        else:
            validated_data['match_type'] = MatchType.M3V3

        match = super().create(validated_data)
        kwargs = {}
        if match.game_mode == GameMode.RANKED:
            kwargs['trophies'] = 0
        if match.game_mode == GameMode.CLASH:
            kwargs['own_goal'] = 0
        for name_team, players in teams.items():
            new_team = Teams.objects.create(match=match, name=name_team)
            for user in players:
                Players.objects.create(user_id=user, match=match, team=new_team, **kwargs)
        return match


class TournamentMatchSerializer(Serializer):
    n = serializers.IntegerField(source='tournament_n')
    winner = serializers.SerializerMethodField()
    looser = serializers.SerializerMethodField()

    class Meta:
        model = Matches
        fields = [
            'id',
            'n',
            'game_duration',
            'winner',
            'looser',
        ]
        read_only_fields = [
            'id',
            'n',
            'game_duration',
            'winner',
            'looser',
        ]

    def get_winner(self, obj):
        if 'users' in self.context:
            return self.context['users'][obj.winner.players.first().user_id]
        return {'id': obj.winner.players.first().user_id}

    def get_looser(self, obj):
        if 'users' in self.context:
            return self.context['users'][obj.looser.players.first().user_id]
        return {'id': obj.winner.players.first().user_id}


class MatchFinishSerializer(Serializer):
    user_id = serializers.IntegerField(required=True, write_only=True)
    finish_reason = serializers.CharField(required=True)

    class Meta:
        model = Matches
        fields = [
            'id',
            'user_id',
            'finish_reason',
            'finished',
        ]
        read_only_fields = [
            'id',
        ]

    @staticmethod
    def validate_finish_reason(value):
        return FinishReason.validate_error(value)

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
        winner.team.score = int(os.environ['GAME_MAX_SCORE'])
        winner.save()
        validated_data['finished'] = True
        result = super().update(instance, validated_data)
        result.finish()
        return result


class ScoreSerializer(Serializer):
    own_goal = serializers.BooleanField(required=False)

    class Meta:
        model = Players
        fields = [
            'score',
            'own_goal',
        ]
        read_only_fields = [
            'score',
        ]

    def to_representation(self, instance):
        return MatchSerializer(instance.match, context={'retrieve_users': False}).data

    def update(self, instance, validated_data):
        if validated_data.pop('own_goal', None) is True:
            instance.score_own_goal()
        else:
            instance.scored()
        return instance
