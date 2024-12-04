from lib_transcendence.auth import IsAuthenticated
from rest_framework import generics
import requests

from matches.models import Matches
from matches.serializers import MatchSerializer, validate_user_id


class MatchCreateView(generics.CreateAPIView):
    serializer_class = MatchSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)
        match = serializer.instance
        r = requests.post('http://localhost:5500/create-game', data={'match_code': match.code})
        self.status_code = r.status_code

class MatchListView(generics.ListAPIView):
    serializer_class = MatchSerializer
    queryset = Matches.objects.all()
    permission_classes = [IsAuthenticated]

    def filter_queryset(self, queryset):
        return queryset.filter(players__user_id=self.kwargs['user_id'])


class MatchRetrieveView(generics.RetrieveAPIView):
    serializer_class = MatchSerializer

    def get_object(self):
        return validate_user_id(self.kwargs.get('user_id'), True)


match_create_view = MatchCreateView.as_view()
match_list_view = MatchListView.as_view()
match_retrieve_view = MatchRetrieveView.as_view()
