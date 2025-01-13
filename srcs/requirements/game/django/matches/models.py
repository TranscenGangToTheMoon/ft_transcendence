from datetime import timedelta, datetime, timezone

from lib_transcendence.exceptions import ServiceUnavailable
from lib_transcendence.services import request_matchmaking
from lib_transcendence import endpoints
from lib_transcendence.game import FinishReason
from django.db import models
from rest_framework.exceptions import APIException

from matches.utils import send_match_result


class Matches(models.Model):
    code = models.CharField(max_length=4, null=True)
    game_mode = models.CharField(max_length=11)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    game_duration = models.DurationField(default=timedelta(minutes=3))
    tournament_id = models.IntegerField(null=True)
    tournament_stage_id = models.IntegerField(null=True)
    tournament_n = models.IntegerField(null=True)
    finish_reason = models.CharField(null=True, default=None, max_length=20)
    finished = models.BooleanField(default=False)

    winner = models.ForeignKey('Teams', null=True, default=None, on_delete=models.SET_NULL, related_name='winner')
    looser = models.ForeignKey('Teams', null=True, default=None, on_delete=models.SET_NULL, related_name='looser')

    def finish(self):
        if self.finish_reason is None:
            self.finish_reason = FinishReason.NORMAL_END
        self.finished = True
        self.code = None
        self.game_duration = datetime.now(timezone.utc) - self.created_at
        self.winner, self.looser = self.teams.order_by('-score')
        self.save()
        if self.tournament_id is not None:
            data = {
                'winner_id': self.winner.players.first().user_id,
                'score_winner': self.winner.score,
                'score_looser': self.looser.score,
                'finish_reason': self.finish_reason,
            }
            try:
                request_matchmaking(endpoints.Matchmaking.ftournament_result_match.format(match_id=self.id), 'PUT', data)
            except APIException:
                raise ServiceUnavailable('matchmaking')
        send_match_result(self)


class Teams(models.Model):
    match = models.ForeignKey(Matches, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    score = models.IntegerField(default=0)

    @property
    def players_count(self):
        return self.players.count()

    def scored(self):
        self.score += 1
        self.save()
        if self.score == 3:
            self.match.finish()


class Players(models.Model):
    user_id = models.IntegerField()
    match = models.ForeignKey(Matches, on_delete=models.CASCADE, related_name='players')
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='players')
    score = models.IntegerField(default=0)

    def scored(self):
        self.score += 1
        self.save()
        self.team.scored()

    def score_own_goal(self):
        other_team = self.match.teams.exclude(id=self.team.id).first()
        other_team.scored()
