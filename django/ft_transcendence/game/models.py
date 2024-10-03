from django.db import models

from user.models import Users


# Create your models here.
class Matches(models.Model):
    game_mode = models.ForeignKey(GameModes, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    teams = models.ManyToManyField('Teams')
    game_duration = models.DurationField()
    state = models.CharField(max_length=20, default=GameState.lobby) # "lobby" - "playing" - "ended"
    winner = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True)
    tournament = models.ForeignKey('Tournaments', on_delete=models.CASCADE, null=True, default=None)


class Teams(models.Model):
    participants = models.ManyToManyField('Players')
    score = models.IntegerField()

    @property
    def players_count(self):
        return len(self.participants.all())


class Players(models.Model):
    user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True)
    ball_touched = models.IntegerField(default=0)
    score_points = models.IntegerField(default=0)
    most_use_spells = models.ForeignKey(Spells, on_delete=models.SET_NULL, null=True)


class Tournaments(models.Model):
    name = models.CharField(max_length=50)
    participants = models.ManyToManyField(Players)
    max_players = models.ForeignKey(MaxPlayersTournament, on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length=20, default=GameState.lobby) # "lobby" - "playing" - "ended"
    rounds = models.ManyToManyField(Matches)

    @property
    def current_round(self):
        return len(self.rounds.all())


class Seasons(models.Model):
    name = models.CharField(max_length=50)
    n = models.IntegerField(default=1)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    @property
    def title(self):
        return f"Season {self.n}"

    @property
    def full_title(self):
        return f"{self.title}: {self.name}"
