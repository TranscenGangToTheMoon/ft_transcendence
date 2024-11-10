from lib_transcendence.auth import get_auth_user
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.utils import generate_code
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from matchmaking.utils import verify_user, get_tournament, verify_place
from tournament.models import Tournaments, TournamentStage, TournamentParticipants


class TournamentGetParticipantsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user_id')

    class Meta:
        model = TournamentParticipants
        fields = [
            'id',
            'creator',
            'join_at',
        ]


class TournamentSerializer(serializers.ModelSerializer):
    participants = TournamentGetParticipantsSerializer(many=True, read_only=True)

    class Meta:
        model = Tournaments
        fields = '__all__'
        read_only_fields = [
            'code',
            'created_at',
            'created_by',
            'is_started',
        ]

    @staticmethod
    def validate_size(value):
        if (value % 4) != 0:
            raise serializers.ValidationError(MessagesException.ValidationError.TOURNAMENT_SIZE)
        if value >= 32:
            raise serializers.ValidationError(MessagesException.ValidationError.TOURNAMENT_MAX_SIZE)
        if value < 4:
            raise serializers.ValidationError(MessagesException.ValidationError.TOURNAMENT_MIN_SIZE)
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        user = get_auth_user(request)

        if user['is_guest']:
            raise PermissionDenied(MessagesException.PermissionDenied.GUEST_CANNOT_CREATE_TOURNAMENT)

        verify_user(user['id'], True)

        validated_data['code'] = generate_code(Tournaments)
        validated_data['created_by'] = user['id']
        result = super().create(validated_data)
        TournamentParticipants.objects.create(user_id=user['id'], trophies=user['trophies'], tournament=result, creator=True)
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

        verify_place(user, tournament, self.context.get('request'))

        if tournament.created_by == user['id']:
            validated_data['creator'] = True
        validated_data['user_id'] = user['id']
        validated_data['trophies'] = user['trophies']
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

    class Meta:
        model = Tournaments
        fields = [
            'name',
            'code',
            'private',
            'n_participants',
            'size',
            'created_by', #todo send ??
        ]

    @staticmethod
    def get_n_participants(obj):
        return obj.participants.count()
