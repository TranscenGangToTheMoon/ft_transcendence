from math import log2

from django.db import models
from django.utils.text import slugify

import GameState
from user.models import Users


# Create your models here.
class Matches(models.Model):
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
    name = models.CharField(max_length=50)
    participants = models.ManyToManyField(Players)
    max_players = models.ForeignKey('TournamentSize', on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length=20, default=GameState.lobby)
    rounds = models.ManyToManyField(Matches)

    @property
    def current_round(self):
        return len(self.rounds.all())


class TournamentSize(models.Model):
    places = models.PositiveSmallIntegerField(default=8)
    nb_rounds = models.IntegerField(default=None, null=True)

    def save(self, *args, **kwargs):
        if self.nb_rounds is None:
            self.nb_rounds = int(log2(self.places))

        super().save(*args, **kwargs)


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


class Ranks(models.Model):
    name = models.CharField(max_length=20)
    trophy = models.IntegerField()


class GameModes(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(unique=True, null=True, default=None)

    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)


class Spells(models.Model):
    name = models.CharField(max_length=20)
    icon = models.FilePathField()
    reload_time = models.DurationField(default=30)
