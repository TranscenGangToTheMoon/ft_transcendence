from lib_transcendence.auth import Authentication
from rest_framework import generics
import requests

from matches.models import Matches
from matches.serializers import MatchSerializer, validate_user_id


class CreateMatchView(generics.CreateAPIView):
    serializer_class = MatchSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)
        match = serializer.instance
        r = requests.post('http://localhost:5500/create-game', data={'match_id': match.id})
        self.status_code = r.status_code

class ListMatchesView(generics.ListAPIView):
    serializer_class = MatchSerializer
    queryset = Matches.objects.all()
    authentication_classes = [Authentication]

    def filter_queryset(self, queryset):
        return queryset.filter(players__user_id=self.kwargs['user_id'])


class MatchRetrieveView(generics.RetrieveAPIView):
    serializer_class = MatchSerializer

    def get_object(self):
        return validate_user_id(self.kwargs.get('user_id'), True)


create_match_view = CreateMatchView.as_view()
list_matches_view = ListMatchesView.as_view()
retrieve_match_view = MatchRetrieveView.as_view()
