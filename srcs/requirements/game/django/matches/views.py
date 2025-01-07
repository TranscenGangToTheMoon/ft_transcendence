import itertools

from lib_transcendence.auth import Authentication
from lib_transcendence.sse_events import create_sse_event, EventCode
from lib_transcendence.exceptions import MessagesException
from rest_framework import generics, views, status
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response

from matches.models import Matches, Players
from matches.serializers import MatchSerializer, validate_user_id, MatchFinishSerializer


class CreateMatchView(generics.CreateAPIView):
    serializer_class = MatchSerializer

    def perform_create(self, serializer):
        users = list(itertools.chain.from_iterable(serializer.validated_data['teams']))
        super().perform_create(serializer)
        create_sse_event(users, EventCode.GAME_START, serializer.data)


class FinishMatchView(generics.UpdateAPIView):
    serializer_class = MatchFinishSerializer
    queryset = Matches.objects.all()

    def get_object(self):
        try:
            return Matches.objects.get(id=self.kwargs['match_id'])
        except Matches.DoesNotExist:
            raise NotFound(MessagesException.NotFound.MATCH)


class ScoreView(views.APIView):

    @staticmethod
    def post(request, *args, **kwargs):
        try:
            player = Players.objects.get(user_id=kwargs['user_id'], match__finished=False)
        except Players.DoesNotExist:
            raise NotFound(MessagesException.NotFound.NOT_BELONG_MATCH)
        own_goal = request.data.get('own_goal')
        if own_goal is True:
            player.own_goal()
        else:
            player.scored()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListMatchesView(generics.ListAPIView):
    serializer_class = MatchSerializer
    queryset = Matches.objects.all()
    authentication_classes = [Authentication]

    def filter_queryset(self, queryset):
        return queryset.filter(players__user_id=self.kwargs['user_id'], finished=True)


class MatchRetrieveView(generics.RetrieveAPIView):
    serializer_class = MatchSerializer

    def get_object(self):
        return validate_user_id(self.kwargs.get('user_id'), True)


create_match_view = CreateMatchView.as_view()
finish_match_view = FinishMatchView.as_view()
score_view = ScoreView.as_view()
list_matches_view = ListMatchesView.as_view()
retrieve_match_view = MatchRetrieveView.as_view()
