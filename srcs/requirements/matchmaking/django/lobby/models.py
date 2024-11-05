from django.db import models
from lib_transcendence.Lobby import MatchType, Teams


class Lobby(models.Model):
    code = models.CharField(max_length=4, unique=True, editable=False)
    max_participants = models.IntegerField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    game_mode = models.CharField(max_length=11)

    match_type = models.CharField(max_length=3)
    bo = models.IntegerField(default=1)

    @property
    def max_team_participants(self):
        if self.match_type == MatchType.m1v1:
            return 1
        return 3

    @property
    def teams_count(self):
        result = {
            Teams.a: self.participants.filter(team=Teams.a).count(),
            Teams.b: self.participants.filter(team=Teams.b).count(),
            Teams.spectator: self.participants.filter(team=Teams.spectator).count()
        }
        return result

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


class LobbyParticipants(models.Model):
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE, related_name='participants')
    is_guest = models.BooleanField(default=False)
    user_id = models.IntegerField(unique=True)
    creator = models.BooleanField(default=False)
    is_ready = models.BooleanField(default=False)
    join_at = models.DateTimeField(auto_now_add=True, editable=False)

    team = models.CharField(default=None, null=True)

    def get_location_id(self):
        return self.lobby.id

    def delete(self, using=None, keep_parents=False):
        # todo inform other players that xxx leave the lobby
        creator = self.creator
        lobby = Lobby.objects.get(id=self.lobby.id)
        super().delete(using=using, keep_parents=keep_parents)
        participants = lobby.participants.filter(is_guest=False)
        if not participants.exists():
            lobby.delete()
            # todo close websocket connection
        elif creator:
            first_join = participants.order_by('join_at').first()
            first_join.creator = True
            first_join.save()
