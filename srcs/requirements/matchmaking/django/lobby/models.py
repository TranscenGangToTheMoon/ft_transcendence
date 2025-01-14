from django.db import models
from lib_transcendence.game import GameMode
from lib_transcendence.lobby import MatchType, Teams
from lib_transcendence.sse_events import EventCode, create_sse_event

from baning.models import delete_banned
from blocking.utils import delete_player_instance
from matchmaking.create_match import create_match
from matchmaking.utils.sse import send_sse_event


class Lobby(models.Model):
    code = models.CharField(max_length=4, unique=True, editable=False)
    max_participants = models.IntegerField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    game_mode = models.CharField(max_length=11)
    ready_to_play = models.BooleanField(default=False)
    is_playing = models.BooleanField(default=False)

    match_type = models.CharField(max_length=3)

    @property
    def max_team_participants(self):
        if self.match_type == MatchType.M1V1:
            return 1
        return 3

    @property
    def count(self):
        return self.participants.count()

    def get_team_count(self, team):
        return self.participants.filter(team=team).count()

    def get_team_user_id(self, team):
        return list(self.participants.filter(team=team).values_list('user_id', flat=True))

    def is_team_full(self, team):
        if team == Teams.SPECTATOR:
            return False
        return self.get_team_count(team) >= self.max_team_participants

    @property
    def is_full(self):
        return self.participants.count() == self.max_participants

    @property
    def is_ready(self):
        qs = self.participants
        if self.game_mode == GameMode.CUSTOM_GAME:
            qs.exclude(team=Teams.SPECTATOR)
            if not self.is_team_full(Teams.A) or not self.is_team_full(Teams.B):
                return False
        return qs.filter(is_ready=False).count() == 0

    def set_ready_to_play(self, value: bool):
        self.ready_to_play = value
        self.save()
        if self.ready_to_play: # todo handle block user
            if self.game_mode == GameMode.CUSTOM_GAME:
                print('COUCOU', flush=True)
                create_match(GameMode.CUSTOM_GAME, self.get_team_user_id(Teams.A), self.get_team_user_id(Teams.B))
            else:
                pass
            self.is_playing = True
            self.save()
            # Lobby.objects.exclude(id=self.id).filter(ready_to_play=True, count=)

    def delete(self, using=None, keep_parents=False):
        delete_banned(self.code)
        super().delete(using=using, keep_parents=keep_parents)


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

    def delete(self, using=None, keep_parents=False, destroy_lobby=False):
        creator = self.creator
        lobby = self.lobby
        delete_player_instance(self.user_id)
        if not destroy_lobby:
            send_sse_event(EventCode.LOBBY_LEAVE, self)
        super().delete(using=using, keep_parents=keep_parents)
        if creator:
            first_join = lobby.participants.filter(is_guest=False).order_by('join_at').first()
            if first_join is None:
                for user_left in lobby.participants.all():
                    create_sse_event(user_left.user_id, EventCode.LOBBY_DESTROY)
                    user_left.delete(destroy_lobby=True)
                lobby.delete()
            else:
                first_join.creator = True
                first_join.save()
                send_sse_event(EventCode.LOBBY_UPDATE_PARTICIPANT, first_join, {'creator': True}, exclude_myself=False)
