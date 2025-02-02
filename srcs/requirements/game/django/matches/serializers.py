from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied

from lib_transcendence.exceptions import MessagesException, Conflict, ResourceExists
from lib_transcendence.game import GameMode, FinishReason
from lib_transcendence.generate import generate_code
from lib_transcendence.lobby import MatchType
from lib_transcendence.serializer import Serializer
from lib_transcendence.users import retrieve_users
from matches.models import Matches, Players


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
                raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG_GAME)
            raise NotFound(MessagesException.NotFound.NOT_BELONG_GAME)


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    trophies = serializers.IntegerField(required=False)


class TeamsSerializer(serializers.Serializer):
    a = UserSerializer(many=True)
    b = UserSerializer(many=True)

    def validate(self, attrs):
        def get_ids(team):
            return [u['id'] for u in attr[team]]

        attr = super().validate(attrs)
        if len(attr['a']) != len(attr['b']):
            raise serializers.ValidationError(MessagesException.ValidationError.TEAMS_NOT_EQUAL)
        if len(attr['a']) not in (1, 3):
            raise serializers.ValidationError(MessagesException.ValidationError.ONLY_1V1_3V3_ALLOWED)
        if len(get_ids('a') + get_ids('b')) != len(set(get_ids('a') + get_ids('b'))):
            raise serializers.ValidationError(MessagesException.ValidationError.IN_BOTH_TEAMS)
        for user in get_ids('a') + get_ids('b'):
            validate_user_id(user)
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
            'match_type',
            'finished',
            'teams',
            'winner',
            'looser',
            'tournament_id',
        ]
        read_only_fields = [
            'id',
            'match_type',
            'finished',
            'created_at',
            'winner',
            'looser',
            'tournament_id',
        ]
        write_only_fields = [
            'game_mode'
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
            if instance.looser is not None:
                representation['looser'] = instance.looser.name
            else:
                representation['looser'] = None
        else:
            representation.pop('winner')
            representation.pop('looser')
        if representation['tournament_id'] is None:
            representation.pop('tournament_id')
        return representation

    def create(self, validated_data):
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
        if match.game_mode == GameMode.CLASH:
            kwargs['own_goal'] = 0
        for name_team, players in teams.items():
            new_team = match.teams.create(name=name_team)
            for user in players:
                if match.game_mode == GameMode.RANKED:
                    kwargs['trophies'] = user['trophies']
                match.players.create(user_id=user['id'], team=new_team, **kwargs)
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
            'finish_reason',
        ]
        read_only_fields = [
            'id',
            'n',
            'game_duration',
            'winner',
            'looser',
            'finish_reason',
        ]

    def get_winner(self, obj):
        if obj.winner is None:
            return None
        user = obj.winner.players.first()
        if user is None:
            return None
        if 'users' in self.context and user.user_id in self.context['users']:
            base = self.context['users'][user.user_id]
        else:
            base = {'id': user.user_id}
        return {**base, 'score': user.score}

    def get_looser(self, obj):
        if obj.looser is None:
            return None
        user = obj.looser.players.first()
        if user is None:
            return None
        if 'users' in self.context and user.user_id in self.context['users']:
            base = self.context['users'][user.user_id]
        else:
            base = {'id': user.user_id}
        return {**base, 'score': user.score}


class MatchFinishSerializer(Serializer):
    user_id = serializers.IntegerField(required=True, write_only=True)
    finish_reason = serializers.CharField(max_length=20, required=True)

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
        player.team.save()
        winner = instance.teams.exclude(id=player.team.id).first()
        winner.score = settings.GAME_MAX_SCORE
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
