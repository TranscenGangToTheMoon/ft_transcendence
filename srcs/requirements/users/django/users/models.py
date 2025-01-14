from datetime import datetime, timezone

from django.db import models
from django.db.models import Q
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
    accept_chat_from = models.CharField(max_length=30, default=AcceptChat.FRIENDS_ONLY)

    is_online = models.BooleanField(default=False)
    game_playing = models.CharField(max_length=5, default=None, null=True)
    last_online = models.DateTimeField(auto_now_add=True)

    def friends(self):
        from friends.models import Friends

        return Friends.objects.filter(Q(user_1=self.id) | Q(user_2=self.id))

    def set_game_playing(self, code=None):
        self.game_playing = code
        self.save()

    def connect(self):
        launch_ping_loop = not self.is_online
        self.is_online = True
        self.last_online = datetime.now(timezone.utc)
        self.save()
        return launch_ping_loop

    def disconnect(self):
        print(f'User {self.id} disconnect', flush=True)

        try:
            request_matchmaking(endpoints.UsersManagement.fdelete_user.format(user_id=self.id), 'DELETE')
        except APIException:
            pass

        self.is_online = False
        self.last_online = datetime.now(timezone.utc)
        self.save()
