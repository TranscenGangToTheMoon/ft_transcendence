from lib_transcendence.auth import get_auth_user
from lib_transcendence.utils import generate_code
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from matchmaking.utils import verify_user, get_tournament, create_match
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
            raise serializers.ValidationError(['Size must be a multiple of 4.'])
        if value > 32:
            raise serializers.ValidationError(['Size must be less than 32.'])
        if value < 4:
            raise serializers.ValidationError(['Size must be greater or equal than 4.'])
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        user = get_auth_user(request)

        if user['is_guest']:
            raise PermissionDenied('Guest cannot create tournament.')

        verify_user(user['id'], False)

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
        tournament = get_tournament(create=True, code=self.context.get('code'))

        if tournament.is_started:
            raise PermissionDenied('Tournament has already started.')

        if tournament.is_full:
            raise PermissionDenied('Tournament is full.')

        user = self.context['auth_user']
        verify_user(user['id'])

        validated_data['user_id'] = user['id']
        validated_data['trophies'] = user['trophies']
        validated_data['tournament'] = tournament
        result = super().create(validated_data)
        # todo websocket: send to tournament chat that user 'xxx' join team

        if int(tournament.size * (80 / 100)) < tournament.participants.count():
            first_stage = tournament.start()
            # todo make seeding
            participants = tournament.participants.all().order_by('seeding')

            for p in participants:
                p.stage = first_stage
                p.save()

            index = 0
            for i in range(int(tournament.size / 2)):
                participants[i].index = index
                participants[i].save()
                if participants.count() > tournament.size - i - 1:
                    create_match(tournament.id, first_stage.id, [[participants[i].user_id], [participants[tournament.size - i - 1].user_id]])
                else:
                    participants[i].win()
                index += 1

        return result
