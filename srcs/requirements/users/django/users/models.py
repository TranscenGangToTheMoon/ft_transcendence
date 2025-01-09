from datetime import datetime

from django.db import models
from lib_transcendence import endpoints
from lib_transcendence.chat import AcceptChat
from lib_transcendence.services import request_matchmaking
from rest_framework.exceptions import APIException

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
    accept_chat_from = models.CharField(max_length=30, default=AcceptChat.friends_only)

    is_online = models.BooleanField(default=False)
    game_playing = models.CharField(max_length=5, default=None, null=True)
    last_online = models.DateTimeField(auto_now_add=True)

    coins = models.IntegerField(default=100)
    trophies = models.IntegerField(default=0)
    current_rank = models.IntegerField(default=None, null=True)
    highest_rank = models.IntegerField(default=None, null=True)

    def set_game_playing(self, code=None):
        self.game_playing = code
        self.save()

    def connect(self):
        print(f'User {self.id} connected', flush=True)
        self.is_online = True
        self.last_online = datetime.now()
        self.save()

    def disconnect(self):
        print(f'User {self.id} disconnect', flush=True)

        try:
            request_matchmaking(endpoints.UsersManagement.fdelete_user.format(user_id=self.id), 'DELETE')
        except APIException:
            pass

        self.is_online = False
        self.last_online = datetime.now()
        self.save()

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
