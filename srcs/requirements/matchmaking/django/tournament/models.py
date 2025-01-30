import time
from datetime import datetime, timezone, timedelta
from threading import Thread

from django.db import models
from rest_framework.exceptions import APIException

from baning.models import delete_banned
from blocking.utils import delete_player_instance
from lib_transcendence import endpoints
from lib_transcendence.services import request_game
from lib_transcendence.sse_events import create_sse_event, EventCode
from lib_transcendence.validate_type import validate_type, surchage_list
from matchmaking.utils.model import ParticipantsPlace
from matchmaking.utils.sse import send_sse_event


class TournamentSize:
    S4 = 4
    S8 = 8
    S16 = 16

    @staticmethod
    def validate(mode):
        return validate_type(mode, TournamentSize)

    @staticmethod
    def attr():
        return surchage_list(TournamentSize)

    def __str__(self):
        return 'Tournament size'


class Tournament(models.Model):
    start_countdown = {
        4: 4,
        8: 7,
        16: 14,
    }

    code = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=50, unique=True)
    size = models.IntegerField(default=16)
    private = models.BooleanField(default=False)
    start_at = models.DateTimeField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField()
    created_by_username = models.CharField(max_length=30)

    def users_id(self, kwargs=None):
        if kwargs is None:
            kwargs = {}
        return list(self.participants.filter(**kwargs).values_list('user_id', flat=True))

    def start_timer(self):
        self.start_at = datetime.now(timezone.utc) + timedelta(seconds=20)
        self.save()
        create_sse_event(self.users_id(), EventCode.TOURNAMENT_START_AT, {'id': self.id, 'start_at': self.start_at}, {'name': self.name})
        Thread(target=self.timer).start()

    def timer(self):
        tournament_id = self.id
        tournament = None
        for _ in range(20):
            try:
                tournament = Tournament.objects.get(id=tournament_id)
            except Tournament.DoesNotExist:
                return
            if not tournament.is_enough_players():
                tournament.cancel_start()
                return
            time.sleep(1)
        tournament.start()

    def cancel_start(self):
        self.start_at = None
        self.save()
        create_sse_event(self.users_id(), EventCode.TOURNAMENT_START_CANCEL, {'id': self.id, 'start_at': None})

    def is_enough_players(self):
        return self.start_countdown[self.size] <= self.participants.count()

    def start(self):
        data = {
            'id': self.id,
            'name': self.name,
            'size': self.size,
            'created_by': self.created_by,
            'participants': [{'id': user.id, 'trophies': user.trophies} for user in self.participants.all()],
        }
        try:
            request_game(endpoints.Game.tournaments, method='POST', data=data)
            self.delete()
        except APIException:
            pass

    @property
    def is_full(self):
        return self.participants.count() == self.size

    def delete(self, using=None, keep_parents=False):
        delete_banned(self.code)
        super().delete(using=using, keep_parents=keep_parents)


class TournamentParticipants(ParticipantsPlace, models.Model):
    user_id = models.IntegerField()
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participants')
    trophies = models.IntegerField()
    creator = models.BooleanField(default=False)
    join_at = models.DateTimeField(auto_now_add=True)

    @property
    def place(self):
        return self.tournament

    def delete(self, using=None, keep_parents=False):
        tournament = self.tournament
        last_member = tournament.participants.count() == 1
        delete_player_instance(self.user_id)
        if not last_member:
            send_sse_event(EventCode.TOURNAMENT_LEAVE, self)
        super().delete(using=using, keep_parents=keep_parents)
        if last_member:
            tournament.delete()
