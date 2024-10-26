from rest_framework import generics, serializers

from game.auth import IsAuthenticated
from matches.models import Matches
from matches.serializers import MatchSerializer


class MatchCreateView(generics.CreateAPIView):
    serializer_class = MatchSerializer


class MatchListView(generics.ListAPIView):
    serializer_class = MatchSerializer
    queryset = Matches.objects.all()
    permission_classes = [IsAuthenticated]

    def filter_queryset(self, queryset):
        user_id = self.kwargs.get('user_id')

        if user_id is None:
            raise serializers.ValidationError({'user_id': ['User id is required.']})

        return queryset.filter(players__user_id=user_id)


match_create_view = MatchCreateView.as_view()
match_list_view = MatchListView.as_view()
