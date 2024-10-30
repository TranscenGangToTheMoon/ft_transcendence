from lib_transcendence.GameMode import GameMode
from rest_framework import generics, serializers

from lobby.models import Lobby, LobbyParticipants
from lobby.serializers import LobbySerializer, LobbyParticipantsSerializer
from matchmaking.utils import get_participants


def get_lobby_participants(lobby, user_id, creator_check=False):
    return get_participants('lobby', LobbyParticipants, lobby, user_id, creator_check)


def get_lobby(code):
    if code is None:
        raise serializers.ValidationError({'code': 'Lobby code is required.'})
    try:
        return Lobby.objects.get(code=code)
    except Lobby.DoesNotExist:
        raise serializers.ValidationError({'code': f"Lobby '{code}' does not exist."})


class LobbyView(generics.CreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Lobby.objects.all()
    serializer_class = LobbySerializer

    def get_object(self):
        participant = get_lobby_participants(None, self.request.user.id, self.request.method != 'GET')
        if self.request.method in ('PUT', 'PATCH') and participant.lobby.game_mode == GameMode.clash:
            raise serializers.ValidationError({'code': 'You cannot update Clash lobby.'})
        return participant.lobby


class LobbyParticipantsView(generics.ListCreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = LobbyParticipants.objects.all()
    serializer_class = LobbyParticipantsSerializer
    lookup_field = 'code'

    def filter_queryset(self, queryset):
        lobby = get_lobby(self.kwargs.get('code'))
        return queryset.filter(lobby_id=lobby.id) # todo change for see Lobby serializer when list

    def get_object(self):
        return get_lobby_participants(get_lobby(self.kwargs.get('code')), self.request.user.id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['code'] = self.kwargs.get('code')
        context['auth_user'] = self.request.data['auth_user']
        return context


class LobbyKickView(generics.DestroyAPIView):
    serializer_class = LobbyParticipantsSerializer
    lookup_field = 'user_id'

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        if user_id is None:
            raise serializers.ValidationError({'detail': 'User id is required.'})

        lobby = get_lobby(self.kwargs.get('code'))

        if user_id == self.request.user.id:
            raise serializers.ValidationError({'detail': 'You cannot kick yourself.'})
        get_lobby_participants(lobby, self.request.user.id, True)

        try:
            return lobby.participants.get(user_id=user_id)
        except LobbyParticipants.DoesNotExist:
            raise serializers.ValidationError({'detail': f"User id '{user_id}' is not participant of this lobby."})


lobby_view = LobbyView.as_view()
lobby_participants_view = LobbyParticipantsView.as_view()
lobby_kick_view = LobbyKickView.as_view()
