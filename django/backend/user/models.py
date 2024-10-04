import random
import string

from django.db import models

from game.models import Ranks, GameModes


# Create your models here.
class Users(models.Model):

    # todo utils:
    # Users.objects.first().chats_set.all()
    # Chats.objects.last().participants.all().exists()

    username = models.CharField(max_length=20, null=True, unique=True)
    password = models.TextField(default=None, null=True)
    picture_profile = models.ForeignKey('PictureProfiles', on_delete=models.SET_NULL, null=True)
    accept_friend_request = models.BooleanField(default=True)

    is_online = models.BooleanField()
    last_online = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    is_guest = models.BooleanField(default=False)
    # ex: Guest79294

    trophy = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    title = models.ForeignKey('Titles', on_delete=models.SET_NULL, null=True)
    rank = models.ForeignKey(Ranks, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if self.username is None:
            self.username = 'Guest' + random.choices(string.digits, k=5)
        super().save(*args, **kwargs)


class FriendRequests(models.Model):
    user_from = models.ForeignKey(Users, on_delete=models.CASCADE)
    user_to = models.ForeignKey(Users, on_delete=models.CASCADE)
    send_at = models.DateTimeField(auto_now_add=True)


class BlockedUsers(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    user_blocked = models.ForeignKey(Users, on_delete=models.CASCADE)
    blocked_at = models.DateTimeField(auto_now_add=True)


class Stats(models.Model):
    # todo: auto update when register new match
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    game_mode = models.ForeignKey(GameModes, on_delete=models.SET_NULL, null=True)
    score_points = models.IntegerField(default=0)
    cashed_points = models.IntegerField(default=0)
    game_played = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    longest_win_streak = models.IntegerField(default=0)


class Titles(models.Model):
    name = models.CharField(max_length=70)


class PictureProfiles(models.Model):
    path = models.FilePathField()
