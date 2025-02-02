from django.db.models.base import ModelBase
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from invite.utils import invite_yourself, validate_participants_for_inviting
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.game import GameMode
from lib_transcendence.lobby import MatchType
from lib_transcendence.permissions import NotGuest
from lib_transcendence.sse_events import create_sse_event, EventCode
from lobby.models import Lobby, LobbyParticipants
from matchmaking.participant import get_participant
from matchmaking.place import get_place
from tournament.models import Tournament, TournamentParticipants


class InviteMixin(generics.CreateAPIView):
    permission_classes = [NotGuest]

    place: ModelBase
    participant: ModelBase

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        invite_yourself(self.kwargs['user_id'], user_id)
        place = get_place(self.place, code=self.kwargs['code'])
        if isinstance(place, Tournament) and place.started:
            raise PermissionDenied(MessagesException.PermissionDenied.INVITE_AFTER_START)
        creator_check = False
        if self.place is Lobby or place.private:
            creator_check = MessagesException.PermissionDenied.INVITE_NOT_CREATOR.format(obj=type(place).__name__.lower())
        get_participant(self.participant, place, user_id, creator_check)
        validate_participants_for_inviting(place, user_id, self.kwargs['user_id'])

        if self.place is Tournament:
            event = EventCode.INVITE_TOURNAMENT
        elif place.game_mode == GameMode.CLASH:
            event = EventCode.INVITE_CLASH
        elif place.match_type == MatchType.M1V1:
            event = EventCode.INVITE_1V1
        else:
            event = EventCode.INVITE_3V3

        create_sse_event(self.kwargs['user_id'], event, {'id': user_id, 'code': place.code}, kwargs={'username': user_id})
        return Response(status=status.HTTP_204_NO_CONTENT)


class LobbyInviteView(InviteMixin):
    place = Lobby
    participant = LobbyParticipants


class TournamentInviteView(InviteMixin):
    place = Tournament
    participant = TournamentParticipants


lobby_invite_view = LobbyInviteView.as_view()
tournament_invite_view = TournamentInviteView.as_view()
