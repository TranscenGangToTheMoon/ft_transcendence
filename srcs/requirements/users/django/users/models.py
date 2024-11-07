from django.db import models
from lib_transcendence.Chat import AcceptChat

from profile_pictures.models import ProfilePictures


class Users(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    username = models.CharField(unique=True, max_length=30)
    is_guest = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    profile_picture = models.ForeignKey(ProfilePictures, on_delete=models.SET_NULL, null=True, blank=True)
    own_profile_pictures = models.ManyToManyField(ProfilePictures, default=None, symmetrical=False, related_name='own_profile_pictures', blank=True)

    accept_friend_request = models.BooleanField(default=True)
    accept_chat_from = models.CharField(max_length=30, default=AcceptChat.only_friends)

    is_online = models.BooleanField(default=False)
    game_playing = models.CharField(max_length=5, default=None, null=True)
    last_online = models.DateTimeField(auto_now_add=True)

    coins = models.IntegerField(default=100)
    trophies = models.IntegerField(default=0)
    current_rank = models.IntegerField(default=None, null=True)
    highest_rank = models.IntegerField(default=None, null=True)

    def __str__(self):
        return f'{self.id} {self.username}'

# class Stats(models.Model):
#     # auto update when register new match
#     user = models.ForeignKey(Users, on_delete=models.CASCADE)
#     game_mode = models.ForeignKey(GameModes, on_delete=models.SET_NULL, null=True)
#     score_points = models.IntegerField(default=0)
#     cashed_points = models.IntegerField(default=0)
#     game_played = models.IntegerField(default=0)
#     win = models.IntegerField(default=0)
#     longest_win_streak = models.IntegerField(default=0)
