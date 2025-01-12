from rest_framework import serializers

from matches.models import Matches
from matches.serializers import MatchSerializer
from tournaments.models import Tournaments
from tournaments.serializers import TournamentSerializer


class DownloadDataSerializer(serializers.Serializer):
    games = serializers.SerializerMethodField()
    tournaments = serializers.SerializerMethodField()

    @staticmethod
    def get_games(obj):
        matches = Matches.objects.filter(finished=True, players__user_id=obj)
        return MatchSerializer(matches, many=True, context={'retrieve_users': False}).data

    @staticmethod
    def get_tournaments(obj):
        matches = Matches.objects.filter(finished=True, players__user_id=obj).exclude(tournament_id=None).values_list('tournament_id', flat=True).distinct()
        tournaments = Tournaments.objects.filter(id__in=matches)
        return TournamentSerializer(tournaments, many=True, context={'retrieve_users': False}).data
