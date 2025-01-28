from rest_framework import generics

from chat.serializers import MessageSerializer
from lib_transcendence.serializer import SerializerAuthContext
from lib_transcendence.sse_events import EventCode
from matchmaking.utils.participant import get_lobby_participant, get_tournament_participant
from matchmaking.utils.place import get_lobby, get_tournament


class MessageMixin(SerializerAuthContext, generics.CreateAPIView):
    serializer_class = MessageSerializer


class LobbyMessageView(MessageMixin):

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['place'] = get_lobby
        context['participant'] = get_lobby_participant
        context['event_code'] = EventCode.LOBBY_MESSAGE
        return context


class TournamentMessageView(MessageMixin):

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['place'] = get_tournament
        context['participant'] = get_tournament_participant
        context['event_code'] = EventCode.TOURNAMENT_MESSAGE
        return context


lobby_message_view = LobbyMessageView.as_view()
tournament_message_view = TournamentMessageView.as_view()
