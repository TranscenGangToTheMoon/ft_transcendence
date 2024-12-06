from lib_transcendence.exceptions import MessagesException
from lib_transcendence.serializer import SerializerKwargsContext
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from blocking.models import Blocked
from blocking.serializer import BlockedSerializer
from lobby.models import LobbyParticipants
from play.models import Players
from tournament.models import TournamentParticipants


class BlockedUserView(SerializerKwargsContext, generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = BlockedSerializer
    authentication_classes = [] # todo remake

    def get_object(self):
        try:
            return Blocked.objects.get(user_id=self.kwargs['user_id'], blocked_user_id=self.kwargs['blocked_user_id'])
        except Blocked.DoesNotExist:
            raise NotFound(MessagesException.NotFound.BLOCKED_INSTANCE)


class DeleteUserView(generics.DestroyAPIView):
    authentication_classes = [] # todo remake

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


blocked_user_view = BlockedUserView.as_view()
delete_user_view = DeleteUserView.as_view()
