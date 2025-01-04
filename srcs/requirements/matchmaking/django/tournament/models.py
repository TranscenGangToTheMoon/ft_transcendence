from datetime import datetime, timezone, timedelta
from math import log2
import time
from threading import Thread

from django.db import models
from lib_transcendence.sse_events import create_sse_event, EventCode
from rest_framework.exceptions import APIException

from baning.models import delete_banned
from blocking.utils import delete_player_instance
from matchmaking.create_match import create_tournament_match
from matchmaking.utils.sse import send_sse_event, start_tournament_sse


class Tournament(models.Model):
    stage_labels = {0: 'final', 1: 'semi-final', 2: 'quarter-final', 3: 'round of 16'}

    code = models.CharField(max_length=4, unique=True, editable=False)
    name = models.CharField(max_length=50, unique=True)
    size = models.IntegerField(default=16)
    private = models.BooleanField(default=False)
    is_started = models.BooleanField(default=False)
    start_at = models.DateTimeField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.IntegerField()
    created_by_username = models.CharField(max_length=30)

    def users_id(self):
        return list(self.participants.all().values_list('user_id', flat=True))

    def start_timer(self):
        self.start_at = datetime.now(timezone.utc) + timedelta(seconds=20)
        self.save()
        create_sse_event(self.users_id(), EventCode.TOURNAMENT_START_AT, {'id': self.id, 'start_at': self.start_at}, {'name': self.name})
        Thread(target=self.timer).start()

    def timer(self):
        for _ in range(20):
            if not self.is_enough_players():
                self.cancel_start()
                return
            if self.is_started:
                return
            time.sleep(1)
        self.start()

    def cancel_start(self):
        self.start_at = None
        self.save()
        try:
            create_sse_event(self.users_id(), EventCode.TOURNAMENT_START_CANCEL, {'id': self.id, 'start_at': None})
        except APIException:
            pass

    def start(self):
        participants = self.participants.all().order_by('seeding')
        self.is_started = True
        self.size = participants.count()
        self.save()
        first_stage = self.stages.create(label=Tournament.get_label(self.n_stage))

        for p in participants:
            p.stage = first_stage
            p.save()

        index = 0
        for i in range(int(self.size / 2)):
            user_1 = participants[i]
            user_1.index = index
            user_1.save()
            k = self.size - i - 1
            if participants.count() > k:
                user_2 = participants[k]
                user_2.index = index
                user_2.save()
            else:
                user_2 = None
            result = self.matches.create(stage=first_stage, user_1=user_1, user_2=user_2)
            index += 1
        start_tournament_sse(self)
        time.sleep(3)
        for matche in self.matches.all():
            matche.create_match()

    def is_enough_players(self):
        return int(self.size * (80 / 100)) <= self.participants.count()

    @staticmethod
    def get_label(n_stage, previous_stage=1):
        return Tournament.stage_labels[n_stage - previous_stage]

    @property
    def is_full(self):
        return self.participants.count() == self.size

    @property
    def n_stage(self):
        return int(log2(self.size))

    def delete(self, using=None, keep_parents=False):
        delete_banned(self.code)
        super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        if self.private:
            name = '*'
        else:
            name = ''
        name += f'{self.code}/{self.name} {self.created_by} ({self.participants.count()}/{self.size})'
        if self.is_started:
            name += ' STARTED'
        return name


class TournamentStage(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='stages')
    label = models.CharField(max_length=50)
    stage = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.tournament.code}/{self.label} ({self.participants.count()})'


class TournamentParticipants(models.Model):
    user_id = models.IntegerField()
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participants')
    stage = models.ForeignKey(TournamentStage, on_delete=models.CASCADE, default=None, null=True, related_name='participants')
    seeding = models.IntegerField(default=None, null=True) #todo make
    index = models.IntegerField(default=None, null=True) #todo make
    still_in = models.BooleanField(default=True)
    creator = models.BooleanField(default=False)
    join_at = models.DateTimeField(auto_now_add=True)
    # todo cans leave the tournament if started

    @property
    def place(self):
        return self.tournament

    def delete(self, using=None, keep_parents=False):
        tournament = self.tournament
        last_member = tournament.participants.count() == 1
        if tournament.is_started:
            self.eliminate() # todo remake ?
        else:
            delete_player_instance(self.user_id)
            if not last_member:
                send_sse_event(EventCode.TOURNAMENT_LEAVE, self)
            super().delete(using=using, keep_parents=keep_parents)
            if last_member:
                tournament.delete()

    def eliminate(self):
        self.still_in = False
        self.save()

    def win(self):
        if self.stage.stage == self.tournament.n_stage:
            return self.user_id
        try:
            next_stage = self.tournament.stages.get(stage=self.stage.stage + 1)
        except TournamentStage.DoesNotExist:
            next_stage = TournamentStage.objects.create(tournament=self.tournament, label=Tournament.get_label(self.tournament.n_stage, self.stage.stage + 1), stage=self.stage.stage + 1)
        self.stage = next_stage
        self.save()
        return None


class TournamentMatches(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    stage = models.ForeignKey(TournamentStage, on_delete=models.CASCADE, related_name='matches')
    game_code = models.CharField(max_length=4, null=True, default=None)
    winner = models.ForeignKey(TournamentParticipants, on_delete=models.CASCADE, related_name='wins', null=True, default=None)
    user_1 = models.ForeignKey(TournamentParticipants, on_delete=models.CASCADE, related_name='matches_1')
    user_2 = models.ForeignKey(TournamentParticipants, on_delete=models.CASCADE, related_name='matches_2', null=True)
    score_winner = models.IntegerField(null=True, default=None)
    score_looser = models.IntegerField(null=True, default=None)
    reason = models.CharField(null=True, default=None, max_length=50)
    finished = models.BooleanField(default=False)

    def create_match(self):
        if self.user_2 is not None:
            if not self.user_1.still_in:
                self.winner = self.user_2
                self.user_2.win()
            else:
                try:
                    self.game_code = create_tournament_match(self.tournament.id, self.stage.id, [[self.user_1.user_id], [self.user_2.user_id]])['code']
                except APIException:
                    self.finish_game() # todo make
        elif self.user_1.still_in:
            self.winner = self.user_1
            self.user_1.win()
        else:
            self.finish_game() # todo make

    def finish_game(self):
        self.finished = True
        self.save()
