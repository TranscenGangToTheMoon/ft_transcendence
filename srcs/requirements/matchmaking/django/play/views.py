from rest_framework import generics, serializers

from play.models import Players
from play.serializers import PlayersSerializer


class PlayMixin(generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = PlayersSerializer

    def get_object(self):
        try:
            return Players.objects.get(user_id=self.request.user.id)
        except Players.DoesNotExist:
            raise serializers.ValidationError({'detail': "You're not currently playing."})


class DuelView(PlayMixin):
    def create(self, request, *args, **kwargs):
        request.data['game_mode'] = 'duel'
        return super().create(request, *args, **kwargs)


class RankedView(PlayMixin):
    def create(self, request, *args, **kwargs):
        request.data['game_mode'] = 'ranked'
        return super().create(request, *args, **kwargs)


duel_view = DuelView.as_view()
ranked_view = RankedView.as_view()
