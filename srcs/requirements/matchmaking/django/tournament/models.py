from datetime import datetime, timezone, timedelta
from math import log2
import time

from django.db import models
from lib_transcendence.Tournament import Tournament

from baning.models import Baned
from blocking.utils import delete_player_instance
from matchmaking.create_match import create_tournament_match


class Tournaments(models.Model):
    code = models.CharField(max_length=4, unique=True, editable=False)
    name = models.CharField(max_length=50, unique=True)
    size = models.IntegerField(default=16)
    private = models.BooleanField(default=False)
    is_started = models.BooleanField(default=False)
    start_at = models.DateTimeField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.IntegerField()
    created_by_username = models.CharField(max_length=30)

    def start_timer(self):
        self.start_at = datetime.now(timezone.utc) + timedelta(seconds=20)
        self.save()
        # todo websocket: send that game start in ...
        # todo est ce que lon peut quiter ?
        # todo si oui est ce qe ca cancel le timer
        # todo 30 sec
        # todo 3 when full (on peu plus quitter)

        time.sleep(20)
        self.start()

    def start(self):
        self.is_started = True
        self.save()
        first_stage = self.stages.create(label=Tournament.get_label(self.n_stage))
        participants = self.participants.all().order_by('seeding')

        for p in participants:
            p.stage = first_stage
            p.save()

        index = 0
        for i in range(int(self.size / 2)):
            participants[i].index = index
            participants[i].save()
            if participants.count() > self.size - i - 1:
                create_tournament_match(self.id, first_stage.id, [[participants[i].user_id], [participants[self.size - i - 1].user_id]])
            else:
                participants[i].win()
            index += 1

    @property
    def is_full(self):
        return self.participants.count() == self.size

    @property
    def n_stage(self):
        return int(log2(self.size))

    def delete(self, using=None, keep_parents=False):
        code = self.code
        super().delete(using=using, keep_parents=keep_parents)
        Baned.objecs.filter(code=code).delete()

    def __str__(self):
        if self.private:
            name = '*'
        else:
            name = ''
        name += f'{self.code}/{self.name} {self.created_by} ({self.participants.count()}/{self.size})'
        if self.is_started:
            name += ' STARTED'
        return name

    str_name = 'tournament'


class TournamentStage(models.Model):
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, related_name='stages')
    label = models.CharField(max_length=50)
    stage = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.tournament.code}/{self.label} ({self.participants.count()})'


class TournamentParticipants(models.Model):
    user_id = models.IntegerField()
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, related_name='participants')
    stage = models.ForeignKey(TournamentStage, on_delete=models.CASCADE, default=None, null=True, related_name='participants')
    seeding = models.IntegerField(default=None, null=True) #todo make
    index = models.IntegerField(default=None, null=True) #todo make
    still_in = models.BooleanField(default=True)
    creator = models.BooleanField(default=False)
    join_at = models.DateTimeField(auto_now_add=True)
    # todo add delete method and inform players that xxx leave the tournament
    # todo cans leave the tournament if started

    def place(self):
        return self.tournament

    def delete(self, using=None, keep_parents=False):
        tournament = self.tournament
        if tournament.is_started:
            self.eliminate()
        else:
            delete_player_instance(self.user_id)
            super().delete(using=using, keep_parents=keep_parents)
            if tournament.participants.count() == 0:
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

    def __str__(self):
        name = f'{self.tournament.code}/ {self.user_id}'
        if self.creator:
            name += '*'
        if self.still_in:
            name += ' in'
        else:
            name += ' eliminate at'
        if self.stage is not None:
            name += ' ' + self.stage.label
        return name

    str_name = 'tournament'
