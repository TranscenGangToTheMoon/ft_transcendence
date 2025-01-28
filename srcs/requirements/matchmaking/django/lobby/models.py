from django.db import models
from django.db.models import Q
from rest_framework.exceptions import APIException

from blocking.models import Blocked
from lib_transcendence.game import GameMode
from lib_transcendence.lobby import MatchType, Teams
from lib_transcendence.sse_events import EventCode, create_sse_event

from baning.models import delete_banned
from blocking.utils import delete_player_instance
from matchmaking.create_match import create_match
from matchmaking.utils.model import ParticipantsPlace
from matchmaking.utils.sse import send_sse_event


class NoLobbyFound(Exception):
    pass


class Lobby(models.Model):
    code = models.CharField(max_length=4, unique=True)
    max_participants = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    game_mode = models.CharField(max_length=11)
    ready_to_play = models.BooleanField(default=False)
    playing_game = models.CharField(max_length=4, null=True, default=None)
    count = models.IntegerField(default=1)
    match_type = models.CharField(max_length=3)

    @property
    def max_team_participants(self):
        if self.match_type == MatchType.M1V1:
            return 1
        return 3

    def get_team_count(self, team):
        return self.participants.filter(team=team).count()

    def get_user_id(self, team=None):
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
            qs = qs.exclude(team=Teams.SPECTATOR)
            if not self.is_team_full(Teams.A) or not self.is_team_full(Teams.B):
                return False
        return qs.filter(is_ready=False).count() == 0

    def set_ready_to_play(self, value: bool):
        self.ready_to_play = value
        self.save()
        if self.ready_to_play:
            self.play()

    def make_team(self, team):
        def block_relation(result_):
            for new_user in result_.participants.all():
                for team_user_id in team:
                    if Blocked.objects.filter(user_id=new_user.user_id, blocked_user_id=team_user_id).exists():
                        return True
            return False

        remain_player = self.max_participants - len(team)
        while remain_player != 0:
            blocked_user = Blocked.objects.filter(user_id__in=team).values_list('blocked_user_id', flat=True)
            result = Lobby.objects.exclude(Q(id__in=self.exclude_lobby) | Q(participants__user_id__in=blocked_user)).filter(game_mode=GameMode.CLASH, ready_to_play=True, count__lte=remain_player)

            exclude_lobby = [r.id for r in result if block_relation(r)]
            result = result.exclude(id__in=exclude_lobby).order_by('count').last()
            if result is None:
                raise NoLobbyFound()
            team += result.get_user_id()
            self.exclude_lobby.append(result.id)
            self.playing_lobby.append(result)
            remain_player = self.max_participants - len(team)
        return team

    def play(self):
        self.playing_lobby = [self]
        if self.game_mode == GameMode.CUSTOM_GAME:
            team_a = self.get_user_id(Teams.A)
            team_b = self.get_user_id(Teams.B)
        else:
            team_a = self.get_user_id()
            team_b = []
            self.exclude_lobby = [self.id]
            try:
                team_a = self.make_team(team_a)
                team_b = self.make_team(team_b)
            except NoLobbyFound:
                return

        try:
            game_code = create_match(self.game_mode, team_a, team_b)['code']
        except APIException:
            return
        for lobby in self.playing_lobby:
            lobby.playing(game_code)
        if self.game_mode == GameMode.CUSTOM_GAME:
            create_sse_event(self.get_user_id(Teams.SPECTATOR), EventCode.LOBBY_SPECTATE_GAME, data={'code': game_code})

    def playing(self, game_code):
        self.participants.all().update(is_ready=False)
        self.playing_game = game_code
        self.set_ready_to_play(False)

    def join(self):
        self.count += 1
        self.save()

    def leave(self):
        self.count -= 1
        self.save()

    def delete(self, using=None, keep_parents=False):
        delete_banned(self.code)
        super().delete(using=using, keep_parents=keep_parents)


class LobbyParticipants(ParticipantsPlace, models.Model):
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE, related_name='participants')
    is_guest = models.BooleanField(default=False)
    user_id = models.IntegerField(unique=True)
    creator = models.BooleanField(default=False)
    is_ready = models.BooleanField(default=False)
    join_at = models.DateTimeField(auto_now_add=True)

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
        lobby.leave()
        if creator:
            first_join = lobby.participants.filter(is_guest=False).order_by('join_at').first()
            if first_join is None:
                users_left = list(lobby.participants.values_list('user_id', flat=True))
                if users_left:
                    create_sse_event(users_left, EventCode.LOBBY_DESTROY)
                lobby.delete()
            else:
                first_join.creator = True
                first_join.save()
                send_sse_event(EventCode.LOBBY_UPDATE_PARTICIPANT, first_join, {'creator': True}, exclude_myself=False)
