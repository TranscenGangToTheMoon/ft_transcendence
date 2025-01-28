from rest_framework import generics
from rest_framework.exceptions import NotFound

from lib_transcendence.auth import Authentication
from lib_transcendence.exceptions import MessagesException
from tournaments.models import Tournaments
from tournaments.serializers import TournamentSerializer


class SaveTournamentView(generics.CreateAPIView):
    serializer_class = TournamentSerializer

    def get_serializer_context(self):
        return {'retrieve_users': False}


class RetrieveTournamentView(generics.RetrieveAPIView):
    serializer_class = TournamentSerializer
    authentication_classes = [Authentication]

    def get_object(self):
        try:
            return Tournaments.objects.get(id=self.kwargs['tournament_id'])
        except Tournaments.DoesNotExist:
            raise NotFound(MessagesException.NotFound.TOURNAMENT)


save_tournament_view = SaveTournamentView.as_view()
retrieve_tournament_view = RetrieveTournamentView.as_view()
