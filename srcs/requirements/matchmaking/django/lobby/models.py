from django.db import models

from lobby.static import team_a, team_b, team_spectator, match_type_1v1


class Lobby(models.Model):
    code = models.CharField(max_length=5, unique=True, editable=False)
    max_participants = models.IntegerField(editable=False) # 3 or 6
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    game_mode = models.CharField(max_length=11) # clash, custom_game

    # Custom settings
    match_type = models.CharField(max_length=3) # 1v1, 3v3
    bo = models.IntegerField(default=1) # bo1 bo3 bo5
    game_time = models.IntegerField(default=300) # in seconds
    # todo other settings

    @property
    def max_team_participants(self):
        if self.match_type == match_type_1v1:
            return 1
        return 3

    @property
    def participants(self):
        return LobbyParticipants.objects.filter(lobby_id=self.id)

    @property
    def teams_count(self):
        participants = self.participants
        result = {
            team_a: participants.filter(team=team_a).count(),
            team_b: participants.filter(team=team_b).count(),
            team_spectator: participants.filter(team=team_a).count()
        }
        return result

    @property
    def is_full(self):
        return self.participants.count() == self.max_participants


class LobbyParticipants(models.Model):
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE)
    lobby_code = models.CharField(max_length=5, editable=False)
    user_id = models.IntegerField(unique=True)
    username = models.CharField(max_length=20)
    is_admin = models.BooleanField(default=False)
    is_ready = models.BooleanField(default=False)
    join_at = models.DateTimeField(auto_now_add=True, editable=False)

    # Custom settings
    team = models.CharField(default=team_a)

    def delete(self, using=None, keep_parents=False):
        is_admin = self.is_admin
        lobby = Lobby.objects.get(id=self.lobby.id)
        super().delete(using=using, keep_parents=keep_parents)
        participants = LobbyParticipants.objects.filter(lobby_id=lobby.id)
        if not participants.exists():
            lobby.delete()
        elif is_admin:
            first_join = participants.order_by('join_at').first()
            first_join.is_admin = True
            first_join.save()
