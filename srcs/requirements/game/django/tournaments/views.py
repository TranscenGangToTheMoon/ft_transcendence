from lib_transcendence.auth import Authentication
from rest_framework import generics

from tournaments.models import Tournaments
from tournaments.serializers import TournamentSerializer


class SaveTournamentView(generics.CreateAPIView):
    serializer_class = TournamentSerializer


class RetrieveTournamentView(generics.RetrieveAPIView):
    queryset = Tournaments.objects.all()
    serializer_class = TournamentSerializer
    lookup_field = 'tournament_id'
    authentication_classes = [Authentication]


save_tournament_view = SaveTournamentView.as_view()
retrieve_tournament_view = RetrieveTournamentView.as_view()
