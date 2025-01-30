from rest_framework import serializers

from blocking.utils import create_player_instance
from lib_transcendence.auth import get_auth_user
from lib_transcendence.generate import generate_code
from lib_transcendence.serializer import Serializer
from matchmaking.utils.participant import get_participants
from matchmaking.utils.place import get_tournament, verify_place
from matchmaking.utils.user import verify_user
from tournament.models import Tournament, TournamentSize, TournamentParticipants


class TournamentSerializer(Serializer):
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
            'start_at',
            'created_at',
            'created_by',
        ]
        read_only_fields = [
            'code',
            'participants',
            'start_at',
            'created_at',
            'created_by',
        ]

    @staticmethod
    def validate_size(value):
        return TournamentSize.validate(value)

    def get_participants(self, obj):
        participants = get_participants(obj)
        self.context['participants'] = {u['id']: u for u in participants}
        return participants

    def create(self, validated_data):
        request = self.context.get('request')
        user = get_auth_user(request)

        verify_user(user['id'], True)

        validated_data['code'] = generate_code(Tournament)
        validated_data['created_by'] = user['id']
        validated_data['created_by_username'] = user['username']
        result = super().create(validated_data)
        create_player_instance(request, TournamentParticipants, user_id=user['id'], tournament=result, creator=True, trophies=user['trophies'])
        return result


class TournamentParticipantsSerializer(Serializer):
    id = serializers.IntegerField(source='user_id', read_only=True)
    tournament = serializers.CharField(max_length=4, source='tournament.code', read_only=True)

    class Meta:
        model = TournamentParticipants
        fields = [
            'id',
            'tournament',
            'creator',
            'join_at',
        ]
        read_only_fields = [
            'id',
            'tournament',
            'creator',
            'join_at',
        ]

    def create(self, validated_data):
        user = self.context['auth_user']
        tournament = get_tournament(create=True, code=self.context['code'])

        # try: todo handle reconnection
        #     user = tournament.participants.get(user_id=user['id'])
        #     user.reconnect()
        #     return user
        # except TournamentParticipants.DoesNotExist:
        #     pass

        verify_place(user, tournament)

        if tournament.created_by == user['id']:
            validated_data['creator'] = True
        validated_data['user_id'] = user['id']
        validated_data['trophies'] = user['trophies']
        validated_data['tournament'] = tournament
        result = super().create(validated_data)
        create_player_instance(self.context['request'])
        return result


class TournamentSearchSerializer(Serializer):
    n_participants = serializers.SerializerMethodField(read_only=True)
    created_by = serializers.CharField(source='created_by_username', read_only=True)

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
