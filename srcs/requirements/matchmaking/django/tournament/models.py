from datetime import datetime, timezone, timedelta
from math import log2
import time
from threading import Thread

from django.db import models
from django.db.models.functions import Random
from lib_transcendence.game import FinishReason
from lib_transcendence.sse_events import create_sse_event, EventCode
from lib_transcendence.validate_type import validate_type, surchage_list
from rest_framework.exceptions import APIException

from baning.models import delete_banned
from blocking.utils import delete_player_instance, model_exists
from lobby.models import LobbyParticipants
from matchmaking.create_match import create_tournament_match, create_tournament_match_not_played
from matchmaking.utils.model import ParticipantsPlace
from matchmaking.utils.sse import send_sse_event, start_tournament_sse
from play.models import Players
from tournament.sse import send_sse_event_finish_match


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
    stage_labels = {0: 'final', 1: 'semi-final', 2: 'quarter-final', 3: 'round of 16'}
    start_countdown = {
        4: 4,
        8: 7,
        16: 14,
    }
    match_order = {
        4: {1: 1, 2: 2},
        8: {1: 1, 2: 3, 3: 4, 4: 2},
        16: {1: 1, 2: 5, 3: 7, 4: 3, 5: 4, 6: 8, 7: 6, 8: 2},
    }

    code = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=50, unique=True)
    size = models.IntegerField(default=16)
    private = models.BooleanField(default=False)
    nb_matches = models.IntegerField(default=1)
    is_started = models.BooleanField(default=False)
    current_stage = models.ForeignKey('TournamentStage', on_delete=models.SET_NULL, default=None, null=True, related_name='current_stage')
    start_at = models.DateTimeField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField()
    created_by_username = models.CharField(max_length=30)
    update_stage = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)

    def users_id(self, kwargs=None):
        if kwargs is None:
            kwargs = {}
        return list(self.participants.filter(connected=True, **kwargs).values_list('user_id', flat=True))

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
            if tournament.is_started:
                return
            elif not tournament.is_enough_players():
                tournament.cancel_start()
                return
            time.sleep(1)
        tournament.start()

    def cancel_start(self):
        self.start_at = None
        self.save()
        create_sse_event(self.users_id(), EventCode.TOURNAMENT_START_CANCEL, {'id': self.id, 'start_at': None})

    def start(self):
        self.is_started = True
        self.start_at = datetime.now(timezone.utc)
        for n_stage in range(int(log2(self.size))):
            self.stages.create(label=Tournament.stage_labels[n_stage], stage=n_stage)
        self.current_stage = self.stages.last()
        self.save()
        first_stage = self.current_stage
        participants = self.participants.all().order_by('-trophies', Random())

        for n, p in enumerate(participants):
            p.seed = n + 1
            p.stage = first_stage
            p.save()

        for i in range(int(self.size / 2)):
            user_1 = participants[i]
            index = self.match_order[self.size][user_1.seed]
            user_1.index = index
            user_1.save()
            k = self.size - i - 1
            if participants.count() > k:
                user_2 = participants[k]
                user_2.index = index
                user_2.save()
            else:
                user_2 = None
            self.matches.create(n=index, stage=first_stage, user_1=user_1, user_2=user_2)
            self.nb_matches = index
        self.save()
        start_tournament_sse(self)
        time.sleep(3)
        for matche in self.matches.all():
            matche.post()

    def finish(self):
        self.finished = True
        self.save()

    def get_nb_matches(self):
        self.nb_matches += 1
        self.save()
        return self.nb_matches

    def is_enough_players(self):
        return self.start_countdown[self.size] <= self.participants.count()

    def set_update_stage(self, value: bool):
        self.update_stage = value
        self.save()

    @property
    def is_full(self):
        return self.participants.count() == self.size

    def delete(self, using=None, keep_parents=False):
        delete_banned(self.code)
        super().delete(using=using, keep_parents=keep_parents)


class TournamentStage(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='stages')
    label = models.CharField(max_length=50)
    stage = models.IntegerField()


class TournamentParticipants(ParticipantsPlace, models.Model):
    user_id = models.IntegerField()
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participants')
    stage = models.ForeignKey(TournamentStage, on_delete=models.CASCADE, default=None, null=True, related_name='participants')
    seed = models.IntegerField(default=None, null=True)
    trophies = models.IntegerField()
    index = models.IntegerField(default=None, null=True)
    still_in = models.BooleanField(default=True)
    creator = models.BooleanField(default=False)
    join_at = models.DateTimeField(auto_now_add=True)
    connected = models.BooleanField(default=True)

    @property
    def place(self):
        return self.tournament

    def delete(self, using=None, keep_parents=False):
        tournament = self.tournament

        if tournament.finished:
            if not self.connected and (model_exists(LobbyParticipants, self.user_id) or model_exists(Players, self.user_id)):
                delete_player_instance(self.user_id)
            super().delete(using=using, keep_parents=keep_parents)
        elif tournament.is_started:
            self.disconnect()
        else:
            last_member = tournament.participants.count() == 1
            delete_player_instance(self.user_id)
            if not last_member and not self.tournament.is_started:
                send_sse_event(EventCode.TOURNAMENT_LEAVE, self)
            super().delete(using=using, keep_parents=keep_parents)
            if last_member:
                tournament.delete()

    def eliminate(self):
        self.still_in = False
        self.save()

    def win(self):
        cur = self.stage.stage
        if cur == 0:
            return True
        self.stage = self.tournament.stages.get(stage=cur - 1)
        self.save()
        return False

    def reconnect(self):
        self.connected = True
        self.save()

    def disconnect(self):
        self.connected = False
        self.eliminate()


class TournamentMatches(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    stage = models.ForeignKey(TournamentStage, on_delete=models.CASCADE, related_name='matches')
    match_id = models.IntegerField(null=True, default=None)
    match_code = models.CharField(max_length=4, null=True, default=None)
    n = models.IntegerField()
    winner = models.ForeignKey(TournamentParticipants, on_delete=models.SET_NULL, related_name='wins', null=True, default=None)
    user_1 = models.ForeignKey(TournamentParticipants, on_delete=models.SET_NULL, related_name='matches_1', null=True)
    user_2 = models.ForeignKey(TournamentParticipants, on_delete=models.SET_NULL, related_name='matches_2', null=True)
    score_winner = models.IntegerField(null=True, default=None)
    score_looser = models.IntegerField(null=True, default=None)
    finish_reason = models.CharField(max_length=20, null=True, default=None)
    finished = models.BooleanField(default=False)

    def post(self):
        if self.user_2 is not None:
            if not self.user_1.still_in:
                create_tournament_match_not_played(self.tournament.id, self.stage.id, self.n, self.user_2)
                self.finish(self.user_2)
            else:
                try:
                    match = create_tournament_match(self.tournament.id, self.stage.id, self.n, self.user_1.user_id, self.user_2.user_id)
                    self.match_id = match['id']
                    self.match_code = match['code']
                    self.save()
                except APIException:
                    self.finish(None)
        elif self.user_1 is not None and self.user_1.still_in:
            create_tournament_match_not_played(self.tournament.id, self.stage.id, self.n, self.user_1)
            self.finish(self.user_1)
        else:
            self.finish(None)

    def finish(self, winner, looser=None, validated_data=None):
        self.finished = True
        self.winner = winner
        self.match_code = None
        self.save()
        tournament = self.tournament
        if validated_data is None:
            if winner is None:
                validated_data = {'score_winner': 0, 'score_looser': 0, 'finish_reason': FinishReason.NO_GAME}
            else:
                validated_data = {'score_winner': 3, 'score_looser': 0, 'finish_reason': FinishReason.GAME_NOT_PLAYED}
        else:
            validated_data.pop('winner_id')
        if winner is None:
            winner_user_id = None
        else:
            winner_user_id = winner.user_id
        if validated_data['finish_reason'] == FinishReason.NORMAL_END:
            finish_reason = ''
        elif validated_data['finish_reason'] == FinishReason.PLAYER_DISCONNECT:
            finish_reason = ' (obviously the other player gave up the game)'
        elif validated_data['finish_reason'] == FinishReason.GAME_NOT_PLAYED:
            finish_reason = ' (yeah, there just was no game)'
        elif validated_data['finish_reason'] == FinishReason.NO_GAME:
            finish_reason = ' (there was no game, so nobody won)'
        else:
            finish_reason = ' (obviously he played against nobody, not too complicated to win)'
        send_sse_event_finish_match(tournament, winner_user_id, 'nobody' if looser is None else looser.user_id, validated_data['score_winner'], validated_data['score_looser'], finish_reason)

        if winner is None and self.stage.stage == 0:
            self.tournament.delete()
            return

        if winner is not None:
            finished = winner.win()
        else:
            finished = False

        if looser is not None:
            looser.eliminate()

        if finished:
            from tournament.utils import finish_tournament

            finish_tournament(self.tournament.id, winner_user_id)
        else:
            from tournament.utils import create_match_new_stage

            Thread(target=create_match_new_stage, args=(self.tournament.id, )).start()
