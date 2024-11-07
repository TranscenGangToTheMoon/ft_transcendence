from math import log2

from django.db import models
from lib_transcendence.Tournament import Tournament


class Tournaments(models.Model):
    code = models.CharField(max_length=4, unique=True, editable=False)
    name = models.CharField(max_length=50, unique=True)
    size = models.IntegerField(default=16)
    is_public = models.BooleanField(default=True)
    is_started = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.IntegerField()

    def start(self):
        # todo websocket: send that game start in ...
        # todo wait 20 seconds before start
        # self.start_at = datetime.now(timezone.utc) + timedelta(seconds=20)
        self.is_started = True
        self.save()
        return TournamentStage.objects.create(tournament=self, label=Tournament.get_label(self.n_stage)) # todo create direclty from self.stage

    @property
    def is_full(self):
        return self.participants.count() == self.size

    @property
    def n_stage(self):
        return int(log2(self.size))

    def __str__(self):
        if not self.is_public:
            name = '*'
        else:
            name = ''
        name += f'{self.code}/{self.name} ({self.participants.count()}/{self.size})'
        if self.is_started:
            name += ' STARTED'
        return name


class TournamentStage(models.Model):
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, related_name='stages')
    label = models.CharField(max_length=50)
    stage = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.tournament.code}/{self.label} ({self.participants.count()})'


class TournamentParticipants(models.Model):
    user_id = models.IntegerField()
    trophies = models.IntegerField()
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, related_name='participants')
    stage = models.ForeignKey(TournamentStage, on_delete=models.CASCADE, default=None, null=True, related_name='participants')
    seeding = models.IntegerField(default=None, null=True)
    index = models.IntegerField(default=None, null=True) #todo make
    still_in = models.BooleanField(default=True)
    creator = models.BooleanField(default=False)
    join_at = models.DateTimeField(auto_now_add=True)
    # todo add delete method and inform players that xxx leave the tournament
    # todo cans leave the tournament if started

    def delete(self, using=None, keep_parents=False):
        tournament = self.tournament
        if tournament.is_started:
            self.eliminate()
        else:
            super().delete(using=using, keep_parents=keep_parents)
            if tournament.participants.count() == 0:
                tournament.delete()

    def get_location_id(self):
        return self.tournament.id

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
        name += ' ' + self.stage.label
        return
