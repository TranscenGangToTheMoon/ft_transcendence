from rest_framework import generics

from tournaments.serializers import TournamentSerializer


class SaveTournamentView(generics.CreateAPIView):
    serializer_class = TournamentSerializer


save_tournament_view = SaveTournamentView.as_view()
