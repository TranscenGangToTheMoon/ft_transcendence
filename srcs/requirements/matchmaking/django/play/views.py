from lib_transcendence.game import GameMode
from lib_transcendence.exceptions import MessagesException
from rest_framework import generics
from rest_framework.exceptions import NotFound

from play.models import Players
from play.serializers import PlayersSerializer


class PlayMixin(generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = PlayersSerializer

    def get_object(self):
        try:
            return Players.objects.get(user_id=self.request.user.id)
        except Players.DoesNotExist:
            raise NotFound(MessagesException.NotFound.NOT_PLAYING)


class DuelView(PlayMixin):
    def create(self, request, *args, **kwargs):
        request.data['game_mode'] = GameMode.duel
        return super().create(request, *args, **kwargs)


class RankedView(PlayMixin):
    def create(self, request, *args, **kwargs):
        request.data['game_mode'] = GameMode.ranked
        return super().create(request, *args, **kwargs)


duel_view = DuelView.as_view()
ranked_view = RankedView.as_view()
