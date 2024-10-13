from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, Manager

from games.models_static import Ranks, GameModes


# Create your models here.
class Titles(models.Model):
    name = models.CharField(max_length=70, unique=True, editable=False)


class UsersQuerySet(models.QuerySet):
    def is_not_guest(self):
        return self.filter(is_guest=False)

    def search(self, query, user=None):
        lookup = Q(username__icontains=query) | Q(password__icontains=query)
        qs = self.is_not_guest().filter(lookup)
        print("query:", query)
        print("qs:", qs)
        if user is not None:
            qs_user = self.filter(django_user=user).filter(lookup)
            print("user qs:", qs_user)
            qs = (qs | qs_user).distinct()
        return qs


class UsersManager(models.Manager):
    def get_queryset(self): #overide functioj
        return UsersQuerySet(self.model, using=self._db)

    def search(self, query, user=None):
        return self.get_queryset().search(query, user=user)


class Stats(models.Model):
    # auto update when register new match
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    game_mode = models.ForeignKey(GameModes, on_delete=models.SET_NULL, null=True)
    score_points = models.IntegerField(default=0)
    cashed_points = models.IntegerField(default=0)
    game_played = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    longest_win_streak = models.IntegerField(default=0)
