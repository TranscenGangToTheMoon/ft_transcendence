from django.db import models

# Create your models here.

# -------------------- STATIC TABLE ---------------------------------------------------------------------------------- #
class GameModes(models.Model):
    name = models.CharField(max_length=30)

class Titles(models.Model):
    name = models.CharField(max_length=70)

class PictureProfiles(models.Model):
    path = models.FilePathField()

class Ranks(models.Model):
    name = models.CharField(max_length=20)
    trophy = models.IntegerField()

class Spells(models.Model):
    name = models.CharField(max_length=20)
    icon = models.FilePathField()

class MaxPlayersTournament(models.Model):
    max_players = models.PositiveSmallIntegerField(default=8) # 4 - 8 - 16
    nb_rounds = models.IntegerField(default=None, null=True)

    def save(self, *args, **kwargs):
        if self.nb_rounds is None:
            self.nb_rounds = int(log2(self.max_players))

        super().save(*args, **kwargs)

# ---------- USER ----------------------------- #

# ---------- CHAT ----------------------------- #


# ---------- GAME ----------------------------- #

# ---------- Stats ----------------------------- #



# ---------- SEASON ----------------------------- #
