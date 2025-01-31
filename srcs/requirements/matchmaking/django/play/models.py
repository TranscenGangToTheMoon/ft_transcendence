from django.db import models

from blocking.utils import delete_player_instance
from lib_transcendence.game import GameMode
from matchmaking.create_match import create_match
from matchmaking.model import ParticipantsPlace

RANGE = 50


class Players(ParticipantsPlace, models.Model):
    user_id = models.IntegerField(unique=True)
    trophies = models.IntegerField()
    game_mode = models.CharField(max_length=10)
    join_at = models.DateTimeField(auto_now_add=True)

    def tag(self):
        if self.game_mode == GameMode.DUEL:
            other_player = Players.objects.exclude(user_id=self.user_id).filter(game_mode=GameMode.DUEL).first()
            if other_player is not None:
                create_match(GameMode.DUEL, self.user_id, other_player.user_id)
                self.delete()
                other_player.delete()
        else:
            ranked_players = Players.objects.exclude(user_id=self.user_id).filter(game_mode=GameMode.RANKED, trophies__gte=self.trophies - RANGE, trophies__lte=self.trophies + RANGE)
            ranked_players = sorted(list(ranked_players), key=lambda x: abs(x.trophies - self.trophies))
            if len(ranked_players) > 0:
                create_match(GameMode.RANKED, {'id': self.user_id, 'trophies': self.trophies}, {'id': ranked_players[0].user_id, 'trophies': ranked_players[0].trophies})
                self.delete()
                ranked_players[0].delete()

    def delete(self, using=None, keep_parents=False):
        delete_player_instance(self.user_id)
        super().delete(using=using, keep_parents=keep_parents)
