from datetime import timedelta, datetime, timezone
from threading import Thread

from django.conf import settings
from django.db import models
from rest_framework.exceptions import APIException

from lib_transcendence import endpoints
from lib_transcendence.exceptions import ServiceUnavailable
from lib_transcendence.game import FinishReason, GameMode
from lib_transcendence.services import request_matchmaking
from lib_transcendence.sse_events import create_sse_event, EventCode
from lib_transcendence.users import retrieve_users
from matches.utils import send_match_result, compute_trophies
from tournaments.models import Tournaments, TournamentStage


class Matches(models.Model):
    code = models.CharField(max_length=4, null=True)
    game_mode = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    match_type = models.CharField(max_length=3)
    game_duration = models.DurationField(default=timedelta(minutes=3))
    send_game_start = models.BooleanField(default=False)
    tournament = models.ForeignKey(Tournaments, null=True, default=None, on_delete=models.CASCADE, related_name='matches')
    tournament_stage = models.ForeignKey(TournamentStage, null=True, default=None, on_delete=models.CASCADE, related_name='matches')
    tournament_n = models.IntegerField(null=True, default=None)
    game_start = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    finish_reason = models.CharField(max_length=20, null=True, default=None)
    finished_at = models.DateTimeField(null=True, default=None)

    winner = models.ForeignKey('Teams', null=True, default=None, on_delete=models.SET_NULL, related_name='winner')
    looser = models.ForeignKey('Teams', null=True, default=None, on_delete=models.SET_NULL, related_name='looser')

    def player_connect(self):
        self.game_start = True
        self.save()

    def start(self):
        from matches.serializers import MatchSerializer
        from matches.timeout import check_timeout

        create_sse_event(self.users_id(), EventCode.GAME_START, MatchSerializer(self).data)
        self.created_at = datetime.now(timezone.utc)
        self.send_game_start = True
        self.save()
        Thread(target=check_timeout, args=(self.id, )).start()

    def users_id(self):
        return list(self.players.all().values_list('user_id', flat=True))

    def finish(self, finish_reason=FinishReason.NORMAL_END):
        if self.finish_reason is None:
            self.finish_reason = finish_reason
        if self.finish_reason == FinishReason.PLAYERS_TIMEOUT and self.game_mode != GameMode.TOURNAMENT:
            self.delete()
            return
        finished_at = datetime.now(timezone.utc)
        self.finished = True
        self.finished_at = finished_at
        self.code = None
        self.game_duration = finished_at - self.created_at
        if self.teams is not None:
            self.winner, self.looser = self.teams.order_by('-score')
        self.save()
        if self.finish_reason == FinishReason.GAME_NOT_PLAYED:
            return
        winner = self.winner.players.first()
        looser = self.looser.players.first()
        if self.game_mode == GameMode.RANKED:
            winner_trophies, looser_trophies = compute_trophies(winner.trophies, looser.trophies)
            winner.set_trophies(winner_trophies)
            looser.set_trophies(-looser_trophies)
        if self.game_mode in [GameMode.CLASH, GameMode.CUSTOM_GAME]:
            try:
                request_matchmaking(endpoints.Matchmaking.lobby_finish_match, 'POST', {'players': self.users_id()})
            except APIException:
                raise ServiceUnavailable('matchmaking')
        send_match_result(self)
        if self.tournament is not None:
            if looser is not None:
                looser = looser.user_id
            self.tournament.finish_match(self, winner, looser)


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
