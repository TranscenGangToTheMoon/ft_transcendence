from django.db import models
from lib_transcendence.game import GameMode

from blocking.utils import delete_player_instance


class Players(models.Model):
    user_id = models.IntegerField(unique=True)
    trophies = models.IntegerField()
    game_mode = models.CharField(max_length=10) # todo try to set available option right here (not in serializer)
    join_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def tag():
        from matchmaking.matchmaking import launch_dual_game
        #print('tag')
        players = Players.objects.all()
        #print('in normal game = ', players.filter(game_mode=GameMode.duel).count())
        if players.filter(game_mode=GameMode.duel).count() >= 2:#change at 1 maybe ?
            launch_dual_game(players.filter(game_mode=GameMode.duel))
            #print('normal taged')
        if players.filter(game_mode=GameMode.ranked).count() == 1:
            pass
            # Thread(target=search_ranked_players()).start()
            #subprocess ??

    def delete(self, using=None, keep_parents=False):
        delete_player_instance(self.user_id)
        super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return str(self.user_id)
