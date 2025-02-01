import time
from datetime import datetime, timezone

from django.db import models

from game.matchmaking import send_finish_match_matchmaking
from lib_transcendence import endpoints
from lib_transcendence.game import FinishReason, GameMode
from lib_transcendence.lobby import MatchType
from lib_transcendence.services import request_users
from lib_transcendence.sse_events import EventCode, create_sse_event


class Tournaments(models.Model):
    stage_labels = {0: 'final', 1: 'semi-final', 2: 'quarter-final', 3: 'round-of-16'}
    match_order = {
        4: {1: 1, 2: 2},
        8: {1: 1, 2: 3, 3: 4, 4: 2},
        16: {1: 1, 2: 5, 3: 7, 4: 3, 5: 4, 6: 8, 7: 6, 8: 2},
    }

    name = models.CharField(max_length=50, unique=True)
    size = models.IntegerField(default=16)
    nb_matches = models.IntegerField(default=1)
    current_stage = models.ForeignKey('TournamentStage', on_delete=models.SET_NULL, default=None, null=True, related_name='current_stage')
    start_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField()
    created_by_username = models.CharField(max_length=15)
    update_stage = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    finish_at = models.DateTimeField(default=None, null=True)

    def finish(self):
        self.finished = True
        self.finish_at = datetime.now(timezone.utc)
        self.save()
        winner_user_id = self.players.filter(still_in=True).first().user_id
        self.players.all().update(still_in=False)
        create_sse_event(self.users_id(), EventCode.TOURNAMENT_FINISH, {'id': self.id}, {'name': self.name, 'username': winner_user_id})
        request_users(endpoints.Users.result_tournament, method='POST', data={'winner': winner_user_id})
        send_finish_match_matchmaking(self.id)

    def main_thread(self):
        time.sleep(5)
        while True:
            time.sleep(3)
            if self.current_stage.stage == 0:
                self.finish()
                return
            matches = self.current_stage.matches.all()
            if matches.filter(finished=False).exists():
                continue

            time.sleep(1)
            stage = self.stages.get(stage=self.current_stage.stage - 1)

            spectate = {}
            previous = None
            for match in matches.order_by('tournament_n'):
                if previous is None:
                    previous = match
                    continue
                self.create_match(self.get_nb_matches(), stage, previous.winner.players.first(), match.winner.players.first())
                spectate[match.id] = match.code
                previous = None

            self.current_stage = stage
            self.save()
            self.start_matches(stage)
            create_sse_event(self.users_id(), EventCode.TOURNAMENT_AVAILABLE_SPECTATE_MATCHES, spectate)

    def finish_match(self, match, winner, looser):
        from tournaments.serializers import TournamentSerializer

        if match.finish_reason == FinishReason.PLAYER_DISCONNECT:
            finish_reason = ' (obviously the other player gave up the game)'
        elif match.finish_reason == FinishReason.GAME_NOT_PLAYED:
            finish_reason = ' (yeah, there just was no game)'
        else:
            finish_reason = ''

        create_sse_event(self.users_id(), EventCode.TOURNAMENT_MATCH_FINISH, TournamentSerializer(self).data, {'winner': winner.user_id, 'looser': looser, 'score_winner': match.winner.score, 'score_looser': match.looser.score, 'finish_reason': finish_reason})
        self.players.get(user_id=winner.user_id).win()
        if looser is not None:
            self.players.get(user_id=looser).eliminate()

    def get_nb_matches(self):
        self.nb_matches += 1
        self.save()
        return self.nb_matches

    def set_update_stage(self, value: bool):
        self.update_stage = value
        self.save()

    def users_id(self):
        return list(self.players.values_list('user_id', flat=True))

    def create_match(self, n, stage, user_1, user_2):
        match = self.matches.create(game_mode=GameMode.TOURNAMENT, match_type=MatchType.M1V1, tournament_n=n, tournament_stage=stage)

        if user_2 is None:
            match.finish(FinishReason.GAME_NOT_PLAYED)
            winner_team = match.teams.create(name='a')
            match.teams.create(name='b')
            match.players.create(user_id=user_1.user_id, team=winner_team)
            match.winner = winner_team
            match.save()
            user_1.win()
        else:
            for name_team, player in (('a', user_1), ('b', user_2)):
                new_team = match.teams.create(name=name_team)
                match.players.create(user_id=player.user_id, team=new_team)

    def start_matches(self, stage, sleep=False):
        if sleep:
            time.sleep(3)
        for matche in self.matches.filter(tournament_stage=stage):
            matche.start()


class TournamentStage(models.Model):
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, related_name='stages')
    label = models.CharField(max_length=50)
    stage = models.IntegerField()


class TournamentPlayers(models.Model):
    user_id = models.IntegerField()
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, related_name='players')
    stage = models.ForeignKey(TournamentStage, on_delete=models.CASCADE, default=None, null=True, related_name='players')
    seed = models.IntegerField(default=None, null=True)
    trophies = models.IntegerField()
    index = models.IntegerField(default=None, null=True)
    still_in = models.BooleanField(default=True)
    creator = models.BooleanField(default=False)
    join_at = models.DateTimeField(auto_now_add=True)

    @property
    def place(self):
        return self.tournament

    def eliminate(self):
        self.still_in = False
        self.save()

    def win(self):
        cur = self.stage.stage
        if cur == 0:
            return
        self.stage = self.tournament.stages.get(stage=cur - 1)
        self.save()
