from lib_transcendence.auth import get_auth_user
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.generate import generate_code
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from blocking.utils import create_player_instance
from matchmaking.utils.participant import get_participants
from matchmaking.utils.place import get_tournament, verify_place
from matchmaking.utils.user import verify_user
from tournament.models import Tournament, TournamentStage, TournamentParticipants


class TournamentSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField(read_only=True)

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
        ]
        read_only_fields = [
            'code',
            'participants',
            'created_at',
            'created_by',
            'is_started',
        ]

    @staticmethod
    def validate_size(value):
        if value >= 32:
            raise serializers.ValidationError(MessagesException.ValidationError.TOURNAMENT_MAX_SIZE)
        if value < 4:
            raise serializers.ValidationError(MessagesException.ValidationError.TOURNAMENT_MIN_SIZE)
        return value

    @staticmethod
    def get_participants(obj):
        return get_participants(obj)

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
        result = super().create(validated_data)
        # todo websocket: send to tournament chat that user 'xxx' join team

        if tournament.size == tournament.participants.count():
            tournament.start()
        # if tournament.start_at is None and int(tournament.size * (80 / 100)) < tournament.participants.count(): todo make
        #     Thread(target=tournament.start_timer).start()

        return result


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


class TournamentResultMatchSerializer(serializers.Serializer):
    tournament_id = serializers.IntegerField()
    game_id = serializers.IntegerField()
    winner = serializers.IntegerField()
    loser = serializers.IntegerField()

    def validate_tournament_id(self, value):
        self.context['tournament'] = get_tournament(id=value)
        return value

    def validate_user(self, value, field: Literal['winner', 'looser']):
        try:
            self.context[field] = self.context['tournament'].participants.get(user_id=value)
        except TournamentParticipants.DoesNotExist:
            raise serializers.ValidationError(MessagesException.NotFound.USER)
        return value

    def validate_winner(self, value):
        return self.validate_user(value, 'winner')

    def validate_looser(self, value):
        return self.validate_user(value, 'looser')

    def create(self, validated_data):
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
        return super().create(validated_data)
