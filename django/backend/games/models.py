import string
import random

from django.db import models

import GameState
from users.models import Users


# Create your models here.
class Matches(models.Model):
    id = models.CharField(default=random.choices(string.digits, k=4), max_length=4, primary_key=True, unique=True, editable=False)
    game_mode = models.ForeignKey('GameModes', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    teams = models.ManyToManyField('Teams')
    game_duration = models.DurationField()
    state = models.CharField(max_length=20, default=GameState.lobby)
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
    most_use_spells = models.ForeignKey('Spells', on_delete=models.SET_NULL, null=True)


class Tournaments(models.Model):
    id = models.CharField(default=random.choices(string.digits, k=4), max_length=4, primary_key=True, unique=True, editable=False)
    name = models.CharField(max_length=50)
    participants = models.ManyToManyField(Players)
    is_public = models.BooleanField(default=True)
    max_players = models.ForeignKey('TournamentSize', on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length=20, default=GameState.lobby)
    rounds = models.ManyToManyField(Matches)

    @property
    def current_round(self):
        return len(self.rounds.all())
