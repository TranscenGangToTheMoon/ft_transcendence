from datetime import datetime, timezone

from lib_transcendence.exceptions import MessagesException
from lib_transcendence.services import requests_game
from rest_framework import generics, serializers
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from matchmaking.utils import get_tournament_participant, get_tournament, create_match, get_kick_participants
from tournament.models import Tournaments, TournamentParticipants
from tournament.serializers import TournamentSerializer, TournamentParticipantsSerializer, TournamentStageSerializer


class TournamentView(generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = Tournaments.objects.all()
    serializer_class = TournamentSerializer

    def get_object(self):
        p = get_tournament_participant(None, self.request.user.id, True)
        if self.request.method != 'GET' and not p.creator:
            raise PermissionDenied()
        return Tournaments.objects.get(id=p.tournament_id)


class TournamentSearchView(generics.ListAPIView):
    serializer_class = TournamentSerializer

    def get_queryset(self):
        query = self.request.data.pop('q', None)
        if query is None:
            raise serializers.ValidationError({'q': [MessagesException.ValidationError.FIELD_REQUIRED]})
        return Tournaments.objects.filter(name__icontains=query)


class TournamentParticipantsView(generics.ListCreateAPIView, generics.DestroyAPIView):
    queryset = TournamentParticipants.objects.all()
    serializer_class = TournamentParticipantsSerializer
    pagination_class = None
    # todo return tournament instance when list

    def filter_queryset(self, queryset):
        tournament = get_tournament(code=self.kwargs.get('code'))
        return queryset.filter(tournament_id=tournament.id)

    def get_object(self):
        return get_tournament_participant(get_tournament(code=self.kwargs.get('code')), self.request.user.id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['code'] = self.kwargs.get('code')
        context['auth_user'] = self.request.data['auth_user']
        return context


class TournamentKickView(generics.DestroyAPIView):
    serializer_class = TournamentParticipantsSerializer
    lookup_field = 'user_id'

    def get_object(self):
        kick_yourself(self.kwargs['user_id'], self.request.user.id)
        tournament = get_tournament(code=self.kwargs.get('code'))
        get_tournament_participant(tournament, self.request.user.id, True)

        if tournament.is_started:
            raise PermissionDenied(MessagesException.PermissionDenied.KICK_AFTER_START)

        return get_kick_participants('tournament', tournament, self.kwargs['user_id'])


class TournamentResultMatchView(generics.CreateAPIView):
    queryset = Tournaments.objects.all()
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        tournament = get_tournament(id=request.data.get('tournament_id'))

        current_stage = None
        finished = None
        for player in ('winner', 'loser'):
            # todo websocket: send to chat tournament that 'xxx' win the game
            user_id = request.data.get(player)
            if user_id is None:
                raise serializers.ValidationError(MessagesException.ValidationError.REQUIRED.format(player.title()))
            try:
                participant = tournament.participants.get(user_id=user_id)
                if current_stage is None:
                    current_stage = participant.stage
                if player == 'winner':
                    finished = participant.win()
                else:
                    participant.eliminate()
            except TournamentParticipants.DoesNotExist:
                raise NotFound(MessagesException.NotFound.USER)

        if finished is not None:
            data = TournamentSerializer(tournament).data
            data['finish_at'] = datetime.now(timezone.utc)
            data['stages'] = TournamentStageSerializer(tournament.stages.all(), many=True).data
            requests_game('tournaments/', data=data)
            tournament.delete()
            # todo websocket: send to chat tournament that 'xxx' win the tournament
            return Response(f'The tournament is over, and player {finished} is the winner!', status=201)

        if not current_stage.participants.filter(still_in=True).exists():
            participants = tournament.participants.filter(still_in=True).order_by('index')
            ct = participants.count()

            for i in range(0, ct, 2):
                create_match(
                    tournament.id,
                    participants[i].stage.id,
                    [
                        [participants[i].user_id],
                        [participants[i + 1].user_id]
                    ]
                )

        return Response('The match result has been successfully recorded.', status=201)


tournament_view = TournamentView.as_view()
tournament_search_view = TournamentSearchView.as_view()
tournament_participants_view = TournamentParticipantsView.as_view()
tournament_kick_view = TournamentKickView.as_view()
tournament_result_match_view = TournamentResultMatchView.as_view()
