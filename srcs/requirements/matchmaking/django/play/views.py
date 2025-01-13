from lib_transcendence.game import GameMode
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.permissions import NotGuest
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

    def perform_create(self, serializer):
        super().perform_create(serializer)
        Players.tag()


class DuelView(PlayMixin):

    def create(self, request, *args, **kwargs):
        request.data['game_mode'] = GameMode.DUEL
        return super().create(request, *args, **kwargs)


class RankedView(PlayMixin):
    permission_classes = [NotGuest]

    def create(self, request, *args, **kwargs):
        request.data['game_mode'] = GameMode.RANKED
        return super().create(request, *args, **kwargs)


duel_view = DuelView.as_view()
ranked_view = RankedView.as_view()
