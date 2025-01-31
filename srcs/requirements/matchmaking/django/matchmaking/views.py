from rest_framework import generics

from matchmaking.serializers import FinishMatchSerializer


class FinishMatchView(generics.CreateAPIView):
    authentication_classes = []
    serializer_class = FinishMatchSerializer


finish_match_view = FinishMatchView.as_view()
