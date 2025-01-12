from rest_framework import generics

from stats.models import GameModeStats, RankedStats
from stats.serializer import StatsSerializer, FinishMatchSerializer, RankedStatsSerializer, FinishTournamentSerializer


class RetrieveStatsView(generics.ListAPIView):
    serializer_class = StatsSerializer
    pagination_class = None

    def get_queryset(self):
        return GameModeStats.objects.filter(user__id=self.request.user.id)


class RetrieveRankedStatsView(generics.ListAPIView):
    serializer_class = RankedStatsSerializer

    def get_queryset(self):
        return RankedStats.objects.filter(user__id=self.request.user.id)


class FinishMatchView(generics.CreateAPIView):
    authentication_classes = []
    serializer_class = FinishMatchSerializer


class FinishTournamentView(generics.CreateAPIView):
    authentication_classes = []
    serializer_class = FinishTournamentSerializer


stats_view = RetrieveStatsView.as_view()
stats_ranked_view = RetrieveRankedStatsView.as_view()
finish_match_view = FinishMatchView.as_view()
finish_tournament_view = FinishTournamentView.as_view()
