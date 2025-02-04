from rest_framework import serializers

from blocking.utils import create_player_instance
from lib_transcendence.auth import get_auth_user
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.game import FinishReason
from lib_transcendence.generate import generate_code
from lib_transcendence.serializer import Serializer
from lib_transcendence.users import retrieve_users
from matchmaking.participant import get_participants
from matchmaking.place import get_tournament, verify_place
from matchmaking.user import verify_user
from tournament.models import Tournament, TournamentSize, TournamentParticipants, TournamentMatches, TournamentStage


class TournamentSerializer(Serializer):
    participants = serializers.SerializerMethodField(read_only=True)
    matches = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tournament
        fields = [
            'id',
            'code',
            'name',
            'participants',
            'size',
            'private',
            'started',
            'start_at',
            'created_at',
            'created_by',
            'matches',
        ]
        read_only_fields = [
            'code',
            'participants',
            'started',
            'start_at',
            'created_at',
            'created_by',
            'matches',
        ]

    @staticmethod
    def validate_size(value):
        return TournamentSize.validate(value)

    def get_participants(self, obj):
        participants = get_participants(obj)
        self.context['participants'] = {u['id']: u for u in participants}
        return participants

    def get_matches(self, obj):
        if obj.started:
            matches = {}
            for stage in obj.stages.all():
                result = TournamentMatchSerializer(stage.matches.all().order_by('n'), many=True, context={'users': self.context['participants']}).data
                matches[stage.label] = result
            if matches:
                return matches
        return None

    def to_representation(self, instance):
        result = super().to_representation(instance)
        if result['matches'] is not None:
            result.pop('participants')
        return result

    def create(self, validated_data):
        request = self.context.get('request')
        user = get_auth_user(request)

        verify_user(user['id'], True)

        validated_data['code'] = generate_code(Tournament)
        validated_data['created_by'] = user['id']
        result = super().create(validated_data)
        create_player_instance(user, TournamentParticipants, user_id=user['id'], tournament=result, creator=True, trophies=user['trophies'])
        return result


class TournamentStageSerializer(Serializer):
    class Meta:
        model = TournamentStage
        fields = [
            'id',
            'label',
            'stage',
        ]


class TournamentParticipantsSerializer(Serializer):
    id = serializers.IntegerField(source='user_id', read_only=True)
    tournament = serializers.CharField(max_length=4, source='tournament.code', read_only=True)

    class Meta:
        model = TournamentParticipants
        fields = [
            'id',
            'tournament',
            'stage',
            'seed',
            'still_in',
            'creator',
            'join_at',
        ]
        read_only_fields = [
            'id',
            'tournament',
            'stage',
            'seed',
            'still_in',
            'creator',
            'join_at',
        ]

    def create(self, validated_data):
        user = self.context['auth_user']
        tournament = get_tournament(create=True, code=self.context['code'])

        try:
            user = tournament.participants.get(user_id=user['id'], connected=False)
            print('Reconnecting user ===================', flush=True)
            user.reconnect()
            return user
        except TournamentParticipants.DoesNotExist:
            pass

        verify_place(user, tournament)
        if tournament.created_by == user['id']:
            validated_data['creator'] = True
        validated_data['user_id'] = user['id']
        validated_data['trophies'] = user['trophies']
        validated_data['tournament'] = tournament
        result = super().create(validated_data)
        create_player_instance(user)
        return result


class TournamentSearchSerializer(Serializer):
    n_participants = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tournament
        fields = [
            'name',
            'code',
            'private',
            'n_participants',
            'size',
            'created_by',
        ]

    @staticmethod
    def get_n_participants(obj):
        return obj.participants.count()


class TournamentMatchSerializer(Serializer):
    winner_id = serializers.IntegerField(required=True, write_only=True)
    winner = serializers.IntegerField(source='winner.user_id', read_only=True)
    score_winner = serializers.IntegerField(required=True)
    score_looser = serializers.IntegerField(required=True)
    finish_reason = serializers.CharField(max_length=20, required=True)
    user_1 = serializers.SerializerMethodField(read_only=True)
    user_2 = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TournamentMatches
        fields = [
            'id',
            'n',
            'match_code',
            'winner',
            'winner_id',
            'score_winner',
            'score_looser',
            'finish_reason',
            'finished',
            'user_1',
            'user_2',
        ]
        read_only_fields = [
            'id',
            'n',
            'winner',
            'match_code',
            'user_1',
            'user_2',
            'finished',
        ]

    def get_user_instance(self, obj, user):
        if user is None:
            return None
        if self.context.get('users') is None:
            users = [obj.user_1.user_id]
            if obj.user_2 is not None:
                users.append(obj.user_2.user_id)
            self.context['users'] = retrieve_users(users, return_type=dict)
        u = self.context['users'].get(user.user_id)
        if u is None:
            return None
        return {**u, **TournamentParticipantsSerializer(user).data}

    def validate_winner_id(self, value):
        if value == self.instance.user_1.user_id:
            self.context['winner'] = self.instance.user_1
            self.context['looser'] = self.instance.user_2
        elif value == self.instance.user_2.user_id:
            self.context['winner'] = self.instance.user_2
            self.context['looser'] = self.instance.user_1
        else:
            raise serializers.ValidationError(MessagesException.ValidationError.NOT_BELONG_MATCH)
        return self.context['winner'].id

    @staticmethod
    def validate_finish_reason(value):
        return FinishReason.validate(value)

    def get_user_1(self, obj):
        return self.get_user_instance(obj, obj.user_1)

    def get_user_2(self, obj):
        return self.get_user_instance(obj, obj.user_2)

    def update(self, instance, validated_data):
        result = super().update(instance, validated_data)
        result.finish(self.context['winner'], self.context['looser'], validated_data)
        return result
