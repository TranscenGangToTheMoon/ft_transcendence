from datetime import datetime, timedelta, timezone
from math import log2

from django.db import models

from tournament.static import get_label


class Tournaments(models.Model):
    code = models.CharField(max_length=4, unique=True, editable=False)
    name = models.CharField(max_length=50, unique=True)
    size = models.IntegerField(default=16)
    is_public = models.BooleanField(default=True)
    start_at = models.DateTimeField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.IntegerField()

    def start(self):
        # todo websocket: send that game start in ...
        self.start_at = datetime.now(timezone.utc) + timedelta(seconds=20)
        self.save()
        return TournamentStage.objects.create(tournament=self, label=get_label(self.n_stage))

    @property
    def is_started(self):
        return self.start_at is not None and self.start_at < datetime.now(timezone.utc)

    @property
    def is_full(self):
        return self.participants.count() == self.size

    @property
    def n_stage(self):
        return int(log2(self.size))


class TournamentStage(models.Model):
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, related_name='stages')
    label = models.CharField(max_length=50)
    stage = models.IntegerField(default=1)


class TournamentParticipants(models.Model):
    user_id = models.IntegerField()
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, related_name='participants')
    stage = models.ForeignKey(TournamentStage, on_delete=models.CASCADE, default=None, null=True, related_name='participants')
    seeding = models.IntegerField(default=None, null=True)
    index = models.IntegerField(default=None, null=True)
    still_in = models.BooleanField(default=True)
    creator = models.BooleanField(default=False)
    join_at = models.DateTimeField(auto_now_add=True)

    def eliminate(self):
        self.still_in = False
        self.save()

    def win(self):
        if self.stage.stage == self.tournament.n_stage:
            return self.user_id
        try:
            next_stage = self.tournament.stages.get(stage=self.stage.stage + 1)
        except TournamentStage.DoesNotExist:
            next_stage = TournamentStage.objects.create(tournament=self.tournament, label=get_label(self.tournament.n_stage, self.stage.stage + 1), stage=self.stage.stage + 1)
        self.stage = next_stage
        self.save()
        return None

#
# class UsersQuerySet(models.QuerySet):
#     def is_not_guest(self):
#         return self.filter(is_guest=False)
#
#     def search(self, query, user=None):
#         lookup = Q(username__icontains=query) | Q(password__icontains=query)
#         qs = self.is_not_guest().filter(lookup)
#         print("query:", query)
#         print("qs:", qs)
#         if user is not None:
#             qs_user = self.filter(django_user=user).filter(lookup)
#             print("user qs:", qs_user)
#             qs = (qs | qs_user).distinct()
#         return qs
#
#
# class UsersManager(models.Manager):
#     def get_queryset(self): #overide functioj
#         return UsersQuerySet(self.model, using=self._db)
#
#     def search(self, query, user=None):
#         return self.get_queryset().search(query, user=user)
#
