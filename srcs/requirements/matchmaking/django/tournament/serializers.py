from rest_framework import serializers

from lobby.models import LobbyParticipants
from matchmaking.auth import get_auth_user, generate_code
from tournament.models import Tournaments, TournamentStage, TournamentParticipants
from tournament.utils import get_tournament, create_match


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
            'start_at',
        ]

    def validate_size(self, value):
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
            raise serializers.ValidationError({'detail': 'Guest cannot create tournament.'})

        valide_participant_create(user['id'])

        validated_data['code'] = generate_code()
        validated_data['created_by'] = user['id']
        result = super().create(validated_data)
        TournamentParticipants.objects.create(user_id=user['id'], tournament=result, creator=True)
        return result

    def update(self, instance, validated_data):
        if instance.is_started:
            raise serializers.ValidationError({'detail': 'Tournament has already started.'})
        return super().update(instance, validated_data)


class TournamentStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentStage
        fields = '__all__'


class TournamentParticipantsSerializer(serializers.ModelSerializer):
    creator = serializers.BooleanField(read_only=True)

    class Meta:
        model = TournamentParticipants
        fields = '__all__'
        read_only_fields = [
            'id',
            'user_id',
            'tournament',
            'stage',
            'seeding',
            'index',
            'still_in',
            'creator',
            'join_at',
        ]

    def create(self, validated_data):
        tournament = get_tournament(code=self.context.get('code'))

        user = self.context['auth_user']
        valide_participant_create(user['id'], join=True)

        if tournament.is_started:
            raise serializers.ValidationError({'code': ['Tournament has already started.']})

        if tournament.is_full:
            raise serializers.ValidationError({'code': ['Tournament is full.']})

        validated_data['user_id'] = user['id']
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
