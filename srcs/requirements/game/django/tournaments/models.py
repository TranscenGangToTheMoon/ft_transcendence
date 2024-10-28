from django.db import models


class Tournaments(models.Model):
    name = models.CharField(max_length=50)
    size = models.IntegerField(default=16)
    created_at = models.DateTimeField(auto_now_add=True)
    start_at = models.DateTimeField()
    finish_at = models.DateTimeField()
    created_by = models.IntegerField()


class TournamentStage(models.Model):
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, related_name='stages')
    label = models.CharField(max_length=50)
    stage = models.IntegerField(default=1)
