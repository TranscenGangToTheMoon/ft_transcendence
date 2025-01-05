from datetime import timedelta, datetime, timezone

from lib_transcendence.services import request_matchmaking
from lib_transcendence import endpoints
from lib_transcendence.game import Reason
from django.db import models


class Matches(models.Model):
    code = models.CharField(max_length=4, unique=True, editable=False)
    game_mode = models.CharField(max_length=11)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    game_duration = models.DurationField(default=timedelta(minutes=3))
    tournament_id = models.IntegerField(null=True)
    reason = models.CharField(null=True, default=None, max_length=20)
    finished = models.BooleanField(default=False)

    def finish_match(self):
        if self.reason is None:
            self.reason = Reason.normal_end
        self.finished = True
        self.game_duration = self.created_at - datetime.now(timezone.utc)
        self.save()
        if self.tournament_id is not None:
            winner, looser = self.teams.order_by('-score')
            data = {
                'winner_id': winner.players.first().user_id,
                'score_winner': winner.score,
                'score_looser': looser.score,
                'reason': self.reason,
            }
            request_matchmaking(endpoints.Matchmaking.ftournament_result_match.format(match_id=self.id), 'PUT', data)


class Teams(models.Model):
    names = ['a', 'b']
    match = models.ForeignKey(Matches, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    score = models.IntegerField(default=0)

    @property
    def players_count(self):
        return self.players.count()

    def scored(self):
        if self.score > 3 or self.match.finished:
            return
        self.score += 1
        self.save()
        if self.score == 3:
            self.match.finish_match()


class Players(models.Model):
    user_id = models.IntegerField()
    match = models.ForeignKey(Matches, on_delete=models.CASCADE, related_name='players')
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='players')
    score = models.IntegerField(default=0)

    def scored(self):
        if self.score > 3 or self.match.finished:
            return
        self.score += 1
        self.save()
        self.team.scored()

    def own_goal(self):
        other_team = self.match.teams.exclude(id=self.team.id).first()
        other_team.scored()
