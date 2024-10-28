from django.db import models

from lobby.static import team_a, team_b, team_spectator, match_type_1v1


class Lobby(models.Model):
    code = models.CharField(max_length=4, unique=True, editable=False)
    max_participants = models.IntegerField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    game_mode = models.CharField(max_length=11)

    match_type = models.CharField(max_length=3)
    bo = models.IntegerField(default=1)
    game_time = models.IntegerField(default=180)

    @property
    def max_team_participants(self):
        if self.match_type == match_type_1v1:
            return 1
        return 3

    @property
    def teams_count(self):
        result = {
            team_a: self.participants.filter(team=team_a).count(),
            team_b: self.participants.filter(team=team_b).count(),
            team_spectator: self.participants.filter(team=team_a).count()
        }
        return result

    @property
    def is_full(self):
        return self.participants.count() == self.max_participants

    @property
    def is_ready(self):
        return self.participants.filter(is_ready=False).count() == 0


class LobbyParticipants(models.Model):
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE, related_name='participants')
    lobby_code = models.CharField(max_length=5, editable=False)
    is_guest = models.BooleanField(default=False)
    user_id = models.IntegerField(unique=True)
    creator = models.BooleanField(default=False)
    is_ready = models.BooleanField(default=False)
    join_at = models.DateTimeField(auto_now_add=True, editable=False)

    team = models.CharField(default=None, null=True)

    def delete(self, using=None, keep_parents=False):
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
