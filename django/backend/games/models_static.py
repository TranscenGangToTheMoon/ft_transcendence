from math import log2

from django.db import models
from django.utils.text import slugify


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
