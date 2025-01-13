from django.db import models
from lib_transcendence.game import GameMode

from stats.utils import get_trophies
from users.models import Users


class GameModeStats(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='stats')
    game_mode = models.CharField(max_length=20)
    scored = models.IntegerField(default=0)
    game_played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    longest_win_streak = models.IntegerField(default=0)
    current_win_streak = models.IntegerField(default=0)
    tournament_wins = models.IntegerField(default=None, null=True)
    own_goals = models.IntegerField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_global(self):
        return self.user.stats.get(game_mode=GameMode.GLOBAL)

    def log(self, score: int, win: bool, own_goals: int | None):
        if self.game_mode != GameMode.GLOBAL:
            self.get_global().log(score, win, own_goals)
        self.game_played += 1
        self.scored += score
        if win:
            self.wins += 1
            self.current_win_streak += 1
            if self.current_win_streak > self.longest_win_streak:
                self.longest_win_streak = self.current_win_streak
        else:
            self.current_win_streak = 0
        if own_goals is not None:
            self.own_goals += own_goals
        self.save()

    def win_tournament(self):
        if self.game_mode != GameMode.GLOBAL:
            self.get_global().win_tournament()
        self.tournament_wins += 1
        self.save()


class RankedStats(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='ranked_stats')
    trophies = models.IntegerField()
    total_trophies = models.IntegerField()
    at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def log(user: Users, trophies: int):
        total_trophies = get_trophies(user) + trophies
        if total_trophies < 0:
            total_trophies = 0
        user.ranked_stats.create(trophies=trophies, total_trophies=total_trophies)
