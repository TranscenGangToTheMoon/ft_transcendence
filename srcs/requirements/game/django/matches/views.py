import os
import time
from threading import Thread

from lib_transcendence.auth import Authentication
from lib_transcendence.game import FinishReason
from lib_transcendence.sse_events import create_sse_event, EventCode
from lib_transcendence.exceptions import MessagesException
from rest_framework import generics
from rest_framework.exceptions import NotFound

from matches.models import Matches, Players
from matches.serializers import MatchSerializer, validate_user_id, MatchFinishSerializer, ScoreSerializer


class CreateMatchView(generics.CreateAPIView):
    serializer_class = MatchSerializer

    def perform_create(self, serializer):
        users = serializer.validated_data['teams']['a'] + serializer.validated_data['teams']['b']
        super().perform_create(serializer)
        create_sse_event(users, EventCode.GAME_START, serializer.data)
        Thread(target=check_timeout, args=(serializer.instance.id, )).start()


def check_timeout(match_id):
    time.sleep(int(os.environ['GAME_PLAYER_CONNECT_TIMEOUT']))
    try:
        print('Checking timeout', flush=True)
        match = Matches.objects.get(id=match_id)
        if not match.game_start:
            print('it FINISH', flush=True)
            match.finish(FinishReason.PLAYERS_TIMEOUT)
    except Matches.DoesNotExist:
        pass


class FinishMatchView(generics.UpdateAPIView):
    serializer_class = MatchFinishSerializer

    def get_object(self):
        try:
            return Matches.objects.get(id=self.kwargs['match_id'])
        except Matches.DoesNotExist:
            raise NotFound(MessagesException.NotFound.MATCH)


class ScoreView(generics.UpdateAPIView):
    serializer_class = ScoreSerializer

    def get_object(self):
        try:
            return Players.objects.get(user_id=self.kwargs['user_id'], match__finished=False)
        except Players.DoesNotExist:
            raise NotFound(MessagesException.NotFound.NOT_BELONG_MATCH)


class ListMatchesView(generics.ListAPIView):
    serializer_class = MatchSerializer
    queryset = Matches.objects.all()
    authentication_classes = [Authentication]

    def filter_queryset(self, queryset):
        return queryset.filter(players__user_id=self.kwargs['user_id'], finished=True)


class UserMatchRetrieveView(generics.RetrieveAPIView):
    serializer_class = MatchSerializer

    def get_object(self):
        return validate_user_id(self.kwargs['user_id'], True)


class MatchRetrieveView(generics.RetrieveAPIView):
    serializer_class = MatchSerializer

    def get_object(self):
        obj = validate_user_id(self.kwargs['user_id'], True, {'match__id': self.kwargs['match_id']})
        obj.start()
        return obj


create_match_view = CreateMatchView.as_view()
finish_match_view = FinishMatchView.as_view()
score_view = ScoreView.as_view()
list_matches_view = ListMatchesView.as_view()
retrieve_user_match_view = UserMatchRetrieveView.as_view()
retrieve_match_view = MatchRetrieveView.as_view()
