from datetime import datetime, timezone

from lib_transcendence import endpoints
from lib_transcendence.auth import get_auth_user
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.generate import generate_code
from lib_transcendence.services import request_game
from lib_transcendence.sse_events import create_sse_event, EventCode
from lib_transcendence.game import Reason
from lib_transcendence.users import retrieve_users
from rest_framework import serializers

from blocking.utils import create_player_instance
from matchmaking.create_match import create_tournament_match
from matchmaking.utils.participant import get_participants
from matchmaking.utils.place import get_tournament, verify_place
from matchmaking.utils.user import verify_user
from tournament.models import Tournament, TournamentStage, TournamentParticipants, TournamentMatches


class TournamentSerializer(serializers.ModelSerializer):
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
            'is_started',
            'start_at',
            'created_at',
            'created_by',
            'matches',
        ]
        read_only_fields = [
            'code',
            'participants',
            'created_at',
            'created_by',
            'is_started',
            'matches',
        ]

    @staticmethod
    def validate_size(value):
        if value >= 32:
            raise serializers.ValidationError(MessagesException.ValidationError.TOURNAMENT_MAX_SIZE)
        if value < 4:
            raise serializers.ValidationError(MessagesException.ValidationError.TOURNAMENT_MIN_SIZE)
        return value

    def get_participants(self, obj):
        if self.context.get('participants') is None:
            self.context['participants'] = get_participants(obj)
        return self.context['participants']

    def get_matches(self, obj):
        if obj.is_started:
            matches = {}
            for stage in obj.stages.all():
                result = TournamentMatchSerializer(stage.matches.all(), many=True, context={'users': self.context['participants']}).data # todo context not work
                matches[stage.label] = result
            return matches
        else:
            return None

    def to_representation(self, instance):
        result = super(TournamentSerializer, self).to_representation(instance)
        if instance.is_started:
            result.pop('participants')
        return result

    def create(self, validated_data):
        request = self.context.get('request')
        user = get_auth_user(request)

        verify_user(user['id'], True)

        validated_data['code'] = generate_code(Tournament)
        validated_data['created_by'] = user['id']
        validated_data['created_by_username'] = user['username']
        result = super().create(validated_data)
        create_player_instance(request, TournamentParticipants, user_id=user['id'], tournament=result, creator=True)
        return result


class TournamentStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentStage
        fields = '__all__'


class TournamentParticipantsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user_id', read_only=True)
    tournament = serializers.CharField(source='tournament.code', read_only=True)

    class Meta:
        model = TournamentParticipants
        fields = [
            'id',
            'tournament',
            'stage',
            'seeding',
            'still_in',
            'creator',
            'join_at',
        ]
        read_only_fields = [
            'id',
            'tournament',
            'stage',
            'seeding',
            'still_in',
            'creator',
            'join_at',
        ]

    def create(self, validated_data):
        user = self.context['auth_user']
        tournament = get_tournament(create=True, code=self.context.get('code'))

        verify_place(user, tournament)

        if tournament.created_by == user['id']:
            validated_data['creator'] = True
        validated_data['user_id'] = user['id']
        validated_data['tournament'] = tournament
        return super().create(validated_data)


class TournamentSearchSerializer(serializers.ModelSerializer):
    n_participants = serializers.SerializerMethodField()
    created_by = serializers.CharField(source='created_by_username')

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


class TournamentMatchSerializer(serializers.ModelSerializer):
    winner = serializers.IntegerField()
    score_winner = serializers.IntegerField()
    score_looser = serializers.IntegerField()
    reason = serializers.IntegerField()
    finished = serializers.BooleanField(required=True)
    user_1 = serializers.SerializerMethodField()
    user_2 = serializers.SerializerMethodField()

    class Meta:
        model = TournamentMatches
        fields = [
            'id',
            'game_code',
            'winner',
            'score_winner',
            'score_looser',
            'reason',
            'finished',
            'user_1',
            'user_2',
        ]
        read_only_fields = [
            'game_code',
            'user_1',
            'user_2',
        ]

    def get_user_instance(self, id):
        if self.context.get('users') is None:
            return None
        for u in self.context['users']:
            if u['id'] == id:
                return u
        return None

    def validate_tournament_id(self, value):
        self.context['tournament'] = get_tournament(id=value)
        return value

    def validate_winner(self, value):
        return self.context['tournament'].participants.get(user_id=value)

    @staticmethod
    def validate_finished(value):
        if value is not True:
            raise serializers.ValidationError(MessagesException.ValidationError.TRUE_ONLY)
        return value

    @staticmethod
    def validate_reason(value):
        return Reason.validate(value)

    def get_user_1(self, obj):
        user = self.get_user_instance(obj.user_1)
        if user is not None:
            return user
        users = [obj.user_1.id]
        if obj.user_2 is not None:
            users.append(obj.user_2.id)
        users_instance = retrieve_users(users)
        print(users_instance, flush=True)
        if len(users_instance) > 1:
            self.context['user_2'] = users_instance[1]
        if len(users_instance) > 0:
            return users_instance[0]
        return None

    def get_user_2(self, obj):
        user = self.get_user_instance(obj.user_2)
        if user is not None:
            return user
        if 'users' in self.context:
            return None
        return self.context.get('user_2')

    def update(self, instance, validated_data):
        result = super().update(instance, validated_data)
        tournament = self.context['tournament']
        participants = list(tournament.participants.all().values_list('user_id', flat=True))
        create_sse_event(participants, EventCode.TOURNAMENT_MATCH_FINISH, validated_data)
        current_stage = self.context['winner'].stage
        finished = self.context['winner'].win()
        self.context['looser'].eliminate()

        if finished is not None:
            data = TournamentSerializer(tournament).data
            data['finish_at'] = datetime.now(timezone.utc)
            data['stages'] = TournamentStageSerializer(tournament.stages.all(), many=True).data
            request_game(endpoints.Game.tournaments, data=data)
            tournament.delete()
            create_sse_event(participants, EventCode.TOURNAMENT_FINISH, {'id': tournament.id, 'name': tournament.name}, {'name': tournament.name, 'username': [validated_data['winner']]})
        else:
            if not current_stage.participants.filter(still_in=True).exists():
                participants = tournament.participants.filter(still_in=True).order_by('index')
                ct = participants.count()

                for i in range(0, ct, 2):
                    create_tournament_match(
                        tournament.id,
                        participants[i].stage.id,
                        [
                            [participants[i].user_id],
                            [participants[i + 1].user_id]
                        ]
                    )
        return result
