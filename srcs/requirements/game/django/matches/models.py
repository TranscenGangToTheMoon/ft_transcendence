from datetime import timedelta, datetime, timezone

from django.db import models
from lib_transcendence.services import requests_tournament_matchmaking


class Matches(models.Model):
    code = models.CharField(max_length=4, unique=True, editable=False)
    game_mode = models.CharField(max_length=11)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    game_duration = models.DurationField(default=timedelta(minutes=3))
    finished = models.BooleanField(default=False)

    tournament_id = models.IntegerField(null=True)
    tournament_stage_id = models.IntegerField(null=True)

    @property
    def winner(self):
        if not self.finished:
            return None
        return self.teams.get(score=max(self.teams.all().values_list('score', flat=True))) # todo remake for work when abandon

    @property
    def finish_str(self):
        if self.finished:
            return 'finish' # ({self.winner} won) '
        return ''

    def finish_match(self):
        if self.finished:
            return
        self.finished = True
        self.game_duration = self.created_at - datetime.now(timezone.utc)
        if self.tournament_id is not None:
            winner, looser = self.players.order_by('-score')
            requests_tournament_matchmaking(self.tournament_id, self.tournament_stage_id, winner.user_id, looser.user_id)
        self.save()

    def __str__(self):
        return f'Match {self.id} {self.finish_str}- [{"], [".join([str(teams) for teams in self.teams.all()])}]'


class Teams(models.Model):
    match = models.ForeignKey(Matches, on_delete=models.CASCADE, related_name='teams')
    score = models.IntegerField(default=0)

    @property
    def players_count(self):
        return self.players.count()

    def __str__(self):
        return f'Team {self.id}[{", ".join([str(user.user_id) for user in self.players.all()])}] - {self.match.code}'


class Players(models.Model):
    user_id = models.IntegerField()
    match = models.ForeignKey(Matches, on_delete=models.CASCADE, related_name='players')
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='players')
    ball_touched = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    def scored(self):
        self.score += 1
        self.save()
        self.team.score += 1
        self.team.save()

    def touch_ball(self):
        self.ball_touched += 1
        self.save()

    def __str__(self):
        return f'User {self.user_id}[{self.team}] - {self.match.code}'
