from rest_framework import generics, status
from rest_framework.response import Response

from lobby.models import LobbyParticipants
from play.models import Players
from tournament.models import TournamentParticipants


class DeleteUserView(generics.DestroyAPIView):
    authentication_classes = []

    def delete(self, request, *args, **kwargs):
        try:
            TournamentParticipants.objects.get(user_id=kwargs['user_id']).delete()
        except TournamentParticipants.DoesNotExist:
            pass
        try:
            LobbyParticipants.objects.get(user_id=kwargs['user_id']).delete()
        except LobbyParticipants.DoesNotExist:
            pass
        try:
            Players.objects.get(user_id=kwargs['user_id']).delete()
        except Players.DoesNotExist:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


delete_user_view = DeleteUserView.as_view()
