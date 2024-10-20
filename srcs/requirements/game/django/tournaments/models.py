from django.db import models


class Tournaments(models.Model):
    code = models.CharField(max_length=4, unique=True, editable=False)
    name = models.CharField(max_length=50)
    participants = models.ManyToManyField(Players)
    is_public = models.BooleanField(default=True)
    max_players = models.IntegerField(default=16)
    # rounds = models.ManyToManyField(Matches)

    @property
    def current_round(self):
        return len(self.rounds.all())


class TournamentRounds(models.Model):
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE)

