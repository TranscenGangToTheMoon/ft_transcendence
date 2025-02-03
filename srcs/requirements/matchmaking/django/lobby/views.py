from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from lib_transcendence.exceptions import MessagesException
from lib_transcendence.game import GameMode
from lib_transcendence.permissions import GuestCannotCreate
from lib_transcendence.serializer import SerializerAuthContext
from lib_transcendence.sse_events import EventCode
from lobby.serializers import LobbySerializer, LobbyParticipantsSerializer, LobbyFinishMatchSerializer
from matchmaking.participant import get_lobby_participant
from matchmaking.place import get_lobby
from matchmaking.sse import send_sse_event


class LobbyView(SerializerAuthContext, generics.CreateAPIView, generics.RetrieveUpdateAPIView):
    serializer_class = LobbySerializer
    permission_classes = [GuestCannotCreate]

    def get_object(self):
        participant = get_lobby_participant(None, self.request.user.id, self.request.method != 'GET', True)
        if self.request.method in ('PUT', 'PATCH') and participant.lobby.game_mode == GameMode.CLASH:
            raise PermissionDenied(MessagesException.PermissionDenied.UPDATE_CLASH_MODE)
        return participant.lobby


class LobbyParticipantsView(SerializerAuthContext, generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = LobbyParticipantsSerializer

    def get_object(self):
        return get_lobby_participant(get_lobby(self.kwargs['code']), self.request.user.id)

    def create(self, request, *args, **kwargs):
        serializer_participant = LobbyParticipantsSerializer(data=request.data, context=self.get_serializer_context())
        if serializer_participant.is_valid():
            self.perform_create(serializer_participant)
            serializer_lobby = LobbySerializer(serializer_participant.instance.lobby, context=self.get_serializer_context())
            return Response(serializer_lobby.data, status=status.HTTP_201_CREATED)
        return Response(serializer_participant.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        send_sse_event(EventCode.LOBBY_JOIN, serializer.instance, serializer.data, self.request)


class LobbyFinishMatchView(generics.CreateAPIView):
    authentication_classes = []
    serializer_class = LobbyFinishMatchSerializer


lobby_view = LobbyView.as_view()
lobby_participants_view = LobbyParticipantsView.as_view()
lobby_finish_match_view = LobbyFinishMatchView.as_view()
