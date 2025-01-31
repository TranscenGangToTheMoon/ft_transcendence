from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from lib_transcendence.exceptions import MessagesException
from matches.serializers import validate_user_id
from tournaments.models import TournamentPlayers
from user_management.serializers import DownloadDataSerializer


class RetrieveGameView(generics.RetrieveAPIView): # todo remake and fix

    def retrieve(self, request, *args, **kwargs):
        validate_user_id(self.kwargs['user_id'], True)
        try:
            TournamentPlayers.objects.get(user_id=self.kwargs['user_id'], tournament__finished=False)
        except TournamentPlayers.DoesNotExist:
            raise NotFound(MessagesException.NotFound.NOT_BELONG_TOURNAMENT)
        return Response(status=HTTP_204_NO_CONTENT)


class DownloadDataView(generics.RetrieveAPIView):
    serializer_class = DownloadDataSerializer
    paginattion_class = None

    def get_object(self):
        return self.kwargs['user_id']


retrieve_game_view = RetrieveGameView.as_view()
export_data_view = DownloadDataView.as_view()
