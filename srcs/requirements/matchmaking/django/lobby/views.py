from rest_framework import generics, serializers

from lobby.models import Lobby, LobbyParticipants
from lobby.serializers import LobbySerializer, LobbyParticipantsSerializer
from lobby.static import lobby_clash


class LobbyCreateUpdateView(generics.CreateAPIView, generics.UpdateAPIView):
    queryset = Lobby.objects.all()
    serializer_class = LobbySerializer

    def get_object(self):
        try:
            participant = LobbyParticipants.objects.get(user_id=self.request.user.id)
            if not participant.is_admin:
                raise serializers.ValidationError({'code': 'You are not admin of this lobby.'})
            lobby = Lobby.objects.get(id=participant.lobby_id)
            if lobby.game_mode == lobby_clash:
                raise serializers.ValidationError({'code': 'You cannot update Clash lobby.'})
            return lobby
        except LobbyParticipants.DoesNotExist:
            raise serializers.ValidationError({'code': 'You are not in any lobby.'})


class LobbyCreateListUpdateDeleteView(generics.ListCreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = LobbyParticipants.objects.all()
    serializer_class = LobbyParticipantsSerializer
    lookup_field = 'code'

    def filter_queryset(self, queryset):
        code = self.kwargs.get('code')
        try:
            lobby_id = Lobby.objects.get(code=code).id
        except Lobby.DoesNotExist:
            raise serializers.ValidationError({'code': f"Lobby '{code}' does not exist."})
        return queryset.filter(lobby_id=lobby_id)

    def get_object(self):
        try:
            return LobbyParticipants.objects.get(user_id=self.request.user.id)
        except LobbyParticipants.DoesNotExist:
            raise serializers.ValidationError({'code': 'You are not participant of this lobby.'})

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['code'] = self.kwargs.get('code')
        context['auth_user'] = self.request.data['auth_user']
        return context


lobby_create_update_view = LobbyCreateUpdateView.as_view()
lobby_create_list_delete_view = LobbyCreateListUpdateDeleteView.as_view()
