from rest_framework import generics

from matches.serializers import MatchSerializer


class MatchCreateView(generics.CreateAPIView):
    # todo secure, only matchmaking can create match
    serializer_class = MatchSerializer


match_create_view = MatchCreateView.as_view()
