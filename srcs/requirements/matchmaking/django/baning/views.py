from rest_framework import generics

from baning.utils import ban_yourself, get_participants_for_baning, banned
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.permissions import NotGuest
from lobby.models import Lobby, LobbyParticipants
from lobby.serializers import LobbyParticipantsSerializer
from matchmaking.participant import get_participant
from matchmaking.place import get_place
from tournament.models import Tournament, TournamentParticipants
from tournament.serializers import TournamentParticipantsSerializer


class BanMixin(generics.DestroyAPIView):
    permission_classes = [NotGuest]
    Place = None
    PlaceParticipant = None

    def get_object(self):
        ban_yourself(self.kwargs['user_id'], self.request.user.id)
        place = get_place(self.Place, code=self.kwargs['code'])
        get_participant(self.PlaceParticipant, place, self.request.user.id, MessagesException.PermissionDenied.BAN_NOT_CREATOR)
        return get_participants_for_baning(place, self.kwargs['user_id'])

    def perform_destroy(self, instance):
        banned(instance)
        super().perform_destroy(instance)


class LobbyBanView(BanMixin):
    serializer_class = LobbyParticipantsSerializer
    Place = Lobby
    PlaceParticipant = LobbyParticipants


class TournamentBanView(BanMixin):
    serializer_class = TournamentParticipantsSerializer
    Place = Tournament
    PlaceParticipant = TournamentParticipants


lobby_ban_view = LobbyBanView.as_view()
tournament_ban_view = TournamentBanView.as_view()
