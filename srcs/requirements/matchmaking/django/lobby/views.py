from lib_transcendence.game import GameMode
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.serializer import SerializerContext
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from lobby.models import Lobby, LobbyParticipants
from lobby.serializers import LobbySerializer, LobbyParticipantsSerializer
from matchmaking.utils import get_lobby, get_lobby_participant, get_kick_participants, kick_yourself


class LobbyView(generics.CreateAPIView, generics.RetrieveUpdateAPIView):
    queryset = Lobby.objects.all()
    serializer_class = LobbySerializer

    def get_object(self):
        participant = get_lobby_participant(None, self.request.user.id, self.request.method != 'GET', True)
        if self.request.method in ('PUT', 'PATCH') and participant.lobby.game_mode == GameMode.clash:
            raise PermissionDenied(MessagesException.PermissionDenied.UPDATE_CLASH_MODE)
        return participant.lobby


class LobbyParticipantsView(SerializerContext, generics.ListCreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = LobbyParticipants.objects.all()
    serializer_class = LobbyParticipantsSerializer
    pagination_class = None
    # todo return tournament instance when create

    def filter_queryset(self, queryset):
        lobby = get_lobby(self.kwargs.get('code'))
        queryset = queryset.filter(lobby_id=lobby.id)
        if self.request.user.id not in queryset.values_list('user_id', flat=True):
            raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG_LOBBY)
        return queryset

    def get_object(self):
        return get_lobby_participant(get_lobby(self.kwargs.get('code')), self.request.user.id)


class LobbyKickView(generics.DestroyAPIView):
    serializer_class = LobbyParticipantsSerializer

    def get_object(self):
        kick_yourself(self.kwargs['user_id'], self.request.user.id)
        lobby = get_lobby(self.kwargs['code'])
        get_lobby_participant(lobby, self.request.user.id, True)
        return get_kick_participants(lobby, self.kwargs['user_id'])


lobby_view = LobbyView.as_view()
lobby_participants_view = LobbyParticipantsView.as_view()
lobby_kick_view = LobbyKickView.as_view()
