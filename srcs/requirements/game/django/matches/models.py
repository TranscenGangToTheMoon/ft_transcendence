from django.db import models

from tournaments.models import Tournaments


class Matches(models.Model):
    code = models.CharField(max_length=4, unique=True, editable=False)
    game_mode = models.CharField(max_length=11, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    game_duration = models.DurationField()
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, null=True, default=None)
    finished = models.BooleanField(default=False)

    @property
    def winner(self):
        if not self.finished:
            return None
        return self.teams_set.get(score=max(self.teams_set.all().values_list('score', flat=True)))

    def finish_game(self, duration):
        self.finished = True
        self.game_duration = duration
        self.save()


class Teams(models.Model):
    match = models.ForeignKey(Matches, on_delete=models.CASCADE)
    score = models.IntegerField()

    @property
    def players_count(self):
        return Players.objects.filter(team=self).count()


class Players(models.Model):
    user_id = models.IntegerField()
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    ball_touched = models.IntegerField(default=0)
    score_points = models.IntegerField(default=0)

    def score(self, score):
        self.score_points += score
        self.save()
        self.team.score += score
        self.team.save()

    def touch_ball(self):
        self.ball_touched += 1
        self.save()
