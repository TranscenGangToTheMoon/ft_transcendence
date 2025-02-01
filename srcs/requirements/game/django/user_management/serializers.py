from rest_framework import serializers

from matches.models import Matches
from matches.serializers import MatchSerializer, validate_user_id
from tournaments.models import Tournaments, TournamentPlayers
from tournaments.serializers import TournamentSerializer


class RetrieveUserPlaceSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    code = serializers.CharField(read_only=True, max_length=4)
    type = serializers.CharField(read_only=True, max_length=11)

    @staticmethod
    def validate_type(value):
        if value not in ['game', 'tournament']:
            raise serializers.ValidationError('Invalid type')
        return value

    def to_representation(self, instance):
        result = {}
        try:
            tournament = TournamentPlayers.objects.get(user_id=instance, tournament__finished=False)
            result['id'] = tournament.tournament_id
            result['type'] = 'tournament'
            result['code'] = None
        except TournamentPlayers.DoesNotExist:
            match = validate_user_id(instance, True)
            result['id'] = match.id
            result['type'] = 'match'
            result['code'] = match.code
        return result


class DownloadDataSerializer(serializers.Serializer):
    matches = serializers.SerializerMethodField()
    tournaments = serializers.SerializerMethodField()

    @staticmethod
    def get_matches(obj):
        matches = Matches.objects.filter(finished=True, players__user_id=obj)
        return MatchSerializer(matches, many=True, context={'retrieve_users': False}).data

    @staticmethod
    def get_tournaments(obj):
        matches = Matches.objects.filter(finished=True, players__user_id=obj).exclude(tournament_id=None).values_list('tournament_id', flat=True).distinct()
        tournaments = Tournaments.objects.filter(id__in=matches)
        return TournamentSerializer(tournaments, many=True, context={'retrieve_users': False}).data
