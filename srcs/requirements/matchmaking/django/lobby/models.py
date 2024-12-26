from django.db import models
from lib_transcendence.game import GameMode
from lib_transcendence.Lobby import MatchType, Teams
from lib_transcendence.sse_events import EventCode
from lib_transcendence.services import create_sse_event

from baning.models import Baned
from blocking.utils import delete_player_instance
from matchmaking.utils.sse import send_sse_event


class Lobby(models.Model):
    code = models.CharField(max_length=4, unique=True, editable=False)
    max_participants = models.IntegerField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    game_mode = models.CharField(max_length=11)
    ready_to_play = models.BooleanField(default=False)

    match_type = models.CharField(max_length=3)

    @property
    def max_team_participants(self):
        if self.match_type == MatchType.m1v1:
            return 1
        return 3

    def get_team_count(self, team):
        return self.participants.filter(team=team).count()

    def is_team_full(self, team):
        if team == Teams.spectator:
            return False
        return self.get_team_count(team) >= self.max_team_participants

    @property
    def is_full(self):
        return self.participants.count() == self.max_participants

    @property
    def is_ready(self):
        qs = self.participants
        if self.game_mode == GameMode.custom_game:
            qs.exclude(team=Teams.spectator)
            if not self.is_team_full(Teams.a) or not self.is_team_full(Teams.b):
                return False
        return qs.filter(is_ready=False).count() == 0

    def set_ready_to_play(self, value: bool):
        self.ready_to_play = value
        self.save()

    def delete(self, using=None, keep_parents=False):
        code = self.code
        super().delete(using=using, keep_parents=keep_parents)
        Baned.objecs.filter(code=code).delete()

    def __str__(self):
        name = f'{self.code}/{self.game_mode} ({self.participants.count()}/{self.max_participants})'
        if self.game_mode == GameMode.custom_game:
            name += ' {' + self.match_type + '}'
        return name


class LobbyParticipants(models.Model):
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE, related_name='participants')
    is_guest = models.BooleanField(default=False)
    user_id = models.IntegerField(unique=True)
    creator = models.BooleanField(default=False)
    is_ready = models.BooleanField(default=False)
    join_at = models.DateTimeField(auto_now_add=True, editable=False)

    team = models.CharField(default=None, null=True)

    @property
    def place(self):
        return self.lobby

    def delete(self, using=None, keep_parents=False):
        creator = self.creator
        lobby = self.lobby
        delete_player_instance(self.user_id)
        send_sse_event(EventCode.LOBBY_LEAVE, self)
        super().delete(using=using, keep_parents=keep_parents)
        if creator:
            first_join = lobby.participants.filter(is_guest=False).order_by('join_at').first()
            if first_join is None:
                for user_left in lobby.participants.all():
                    create_sse_event(user_left.user_id, EventCode.LOBBY_BAN)
                lobby.delete()
            else:
                first_join.creator = True
                first_join.save()
                send_sse_event(EventCode.LOBBY_UPDATE, first_join, {'creator': True}, exclude_myself=False)

    def __str__(self):
        name = f'{self.lobby.code}/{self.lobby.game_mode} {self.user_id}'
        if self.creator:
            name += '*'
        if self.is_ready:
            name += ' ready'
        if self.team is not None:
            name += f" '{self.team}'"
        return name
