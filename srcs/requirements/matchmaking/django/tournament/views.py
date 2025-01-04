from threading import Thread
from typing import Literal

from django.db.models import Q
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.permissions import GuestCannotCreate
from lib_transcendence.serializer import SerializerAuthContext
from lib_transcendence.sse_events import EventCode
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from blocking.models import Blocked
from blocking.utils import create_player_instance, delete_player_instance
from matchmaking.utils.participant import get_tournament_participant
from matchmaking.utils.place import get_tournament
from matchmaking.utils.sse import send_sse_event
from tournament.models import Tournament, TournamentParticipants
from tournament.serializers import TournamentSerializer, TournamentParticipantsSerializer, TournamentSearchSerializer, TournamentMatchSerializer


class TournamentView(generics.CreateAPIView, generics.RetrieveAPIView):
    serializer_class = TournamentSerializer
    permission_classes = [GuestCannotCreate]

    def get_object(self):
        try:
            return Tournament.objects.get(id=get_tournament_participant(None, self.request.user.id, from_place=True).tournament_id)
        except TournamentParticipants.DoesNotExist:
            return NotFound(MessagesException.NotFound.TOURNAMENT)


class TournamentSearchView(generics.ListAPIView):
    serializer_class = TournamentSearchSerializer

    def get_queryset(self):
        def get_blocked_users(kwargs: Literal['user_id', 'blocked_user_id']):
            if kwargs == 'user_id':
                create_player_instance(self.request)
                values_list = 'blocked_user_id'
            else:
                values_list = 'user_id'
            blocked_results = list(Blocked.objects.filter(**{kwargs: self.request.user.id}).values_list(values_list, flat=True))
            if kwargs == 'user_id':
                delete_player_instance(user_id=self.request.user.id)
            return blocked_results

        query = self.request.query_params.get('q')
        if query is None:
            query = ''
        results = Tournament.objects.filter(Q(private=False) | Q(created_by=self.request.user.id), name__icontains=query, is_started=False)
        exclude_blocked = get_blocked_users('user_id') + get_blocked_users('blocked_user_id')
        return results.exclude(created_by__in=exclude_blocked)


class TournamentParticipantsView(SerializerAuthContext, generics.ListCreateAPIView, generics.DestroyAPIView):
    queryset = TournamentParticipants.objects.all()
    serializer_class = TournamentParticipantsSerializer
    pagination_class = None

    def filter_queryset(self, queryset):
        tournament = get_tournament(code=self.kwargs['code'])
        queryset = queryset.filter(tournament_id=tournament.id)
        if not queryset.filter(user_id=self.request.user.id).exists():
            raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG_TOURNAMENT)
        return queryset

    def get_object(self):
        return get_tournament_participant(get_tournament(code=self.kwargs['code']), self.request.user.id)

    def create(self, request, *args, **kwargs):
        serializer_participant = TournamentParticipantsSerializer(data=request.data, context=self.get_serializer_context())
        if serializer_participant.is_valid():
            self.perform_create(serializer_participant)
            serializer_tournament = TournamentSerializer(serializer_participant.instance.tournament, context=self.get_serializer_context())
            return Response(serializer_tournament.data, status=status.HTTP_201_CREATED)
        return Response(serializer_participant.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        send_sse_event(EventCode.TOURNAMENT_JOIN, serializer.instance, serializer.data, self.request)

        tournament = serializer.instance.tournament
        if tournament.size == tournament.participants.count():
            Thread(target=tournament.start).start()
        elif tournament.start_at is None and tournament.is_enough_players():
            tournament.start_timer()


class TournamentResultMatchView(generics.UpdateAPIView):
    permission_classes = [AllowAny]
    serializers_class = TournamentMatchSerializer


tournament_view = TournamentView.as_view()
tournament_search_view = TournamentSearchView.as_view()
tournament_participants_view = TournamentParticipantsView.as_view()
tournament_result_match_view = TournamentResultMatchView.as_view()
