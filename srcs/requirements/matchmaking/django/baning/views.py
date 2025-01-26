from django.core.exceptions import PermissionDenied
from rest_framework import generics
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.permissions import NotGuest

from baning.utils import ban_yourself, get_participants_for_baning, banned
from lobby.serializers import LobbyParticipantsSerializer
from matchmaking.utils.participant import get_lobby_participant, get_tournament_participant
from matchmaking.utils.place import get_lobby, get_tournament
from tournament.serializers import TournamentParticipantsSerializer


class BanMixin(generics.DestroyAPIView):
    permission_classes = [NotGuest]

    def perform_destroy(self, instance):
        banned(instance)
        super().perform_destroy(instance)


class LobbyBanView(BanMixin):
    serializer_class = LobbyParticipantsSerializer

    def get_object(self):
        ban_yourself(self.kwargs['user_id'], self.request.user.id)
        lobby = get_lobby(self.kwargs['code'])
        get_lobby_participant(lobby, self.request.user.id, MessagesException.PermissionDenied.BAN_NOT_CREATOR)
        return get_participants_for_baning(lobby, self.kwargs['user_id'])


class TournamentBanView(BanMixin):
    serializer_class = TournamentParticipantsSerializer

    def get_object(self):
        ban_yourself(self.kwargs['user_id'], self.request.user.id)
        tournament = get_tournament(code=self.kwargs.get('code'))
        get_tournament_participant(tournament, self.request.user.id, MessagesException.PermissionDenied.BAN_NOT_CREATOR)

        if tournament.is_started:
            raise PermissionDenied(MessagesException.PermissionDenied.BAN_AFTER_START)

        return get_participants_for_baning(tournament, self.kwargs['user_id'])


lobby_ban_view = LobbyBanView.as_view()
tournament_ban_view = TournamentBanView.as_view()
