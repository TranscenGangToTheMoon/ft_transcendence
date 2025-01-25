from datetime import timedelta, datetime, timezone

from django.conf import settings
from lib_transcendence.exceptions import ServiceUnavailable
from lib_transcendence.services import request_matchmaking
from lib_transcendence import endpoints
from lib_transcendence.game import FinishReason, GameMode
from django.db import models
from rest_framework.exceptions import APIException
from lib_transcendence.users import retrieve_users

from matches.utils import send_match_result, compute_trophies


class Matches(models.Model):
    code = models.CharField(max_length=4, null=True)
    game_mode = models.CharField(max_length=11)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    match_type = models.CharField(max_length=3)
    game_duration = models.DurationField(default=timedelta(minutes=3))
    tournament_id = models.IntegerField(null=True, default=None)
    tournament_stage_id = models.IntegerField(null=True, default=None)
    tournament_n = models.IntegerField(null=True, default=None)
    game_start = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    finish_reason = models.CharField(max_length=20, null=True, default=None)
    finished_at = models.DateTimeField(null=True, default=None)

    winner = models.ForeignKey('Teams', null=True, default=None, on_delete=models.SET_NULL, related_name='winner')
    looser = models.ForeignKey('Teams', null=True, default=None, on_delete=models.SET_NULL, related_name='looser')

    def start(self):
        self.game_start = True
        self.save()

    def users_id(self):
        return list(self.players.all().values_list('user_id', flat=True))

    def finish(self, finish_reason=FinishReason.NORMAL_END):
        if self.finish_reason is None:
            self.finish_reason = finish_reason
        if self.finish_reason == FinishReason.PLAYERS_TIMEOUT:
            self.delete()
            return
        finished_at = datetime.now(timezone.utc)
        self.finished = True
        self.finished_at = finished_at
        self.code = None
        self.game_duration = finished_at - self.created_at
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
        if self.game_mode == GameMode.RANKED:
            player = retrieve_users(self.users_id(), return_type=dict)
            winner = self.winner.players.first()
            looser = self.looser.players.first()
            winner_trophies, looser_trophies = compute_trophies(player[winner.user_id]['trophies'], player[looser.user_id]['trophies'])
            winner.set_trophies(winner_trophies)
            looser.set_trophies(-looser_trophies)
        if self.game_mode in [GameMode.CLASH, GameMode.CUSTOM_GAME]:
            try:
                request_matchmaking(endpoints.Matchmaking.lobby_finish_match, 'POST', {'players': self.users_id()})
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
        if self.score == settings.GAME_MAX_SCORE:
            self.match.finish()


class Players(models.Model):
    user_id = models.IntegerField()
    match = models.ForeignKey(Matches, on_delete=models.CASCADE, related_name='players')
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='players')
    score = models.IntegerField(default=0)
    trophies = models.IntegerField(null=True, default=None)
    own_goal = models.IntegerField(default=0)

    def scored(self):
        self.score += 1
        self.save()
        self.team.scored()

    def score_own_goal(self):
        self.own_goal += 1
        self.save()
        other_team = self.match.teams.exclude(id=self.team.id).first()
        other_team.scored()

    def set_trophies(self, trophies):
        self.trophies = trophies
        self.save()
