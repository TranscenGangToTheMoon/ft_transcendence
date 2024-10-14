from django.db import models

from profile_pictures.models import ProfilePictures


class Users(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    username = models.CharField(unique=True, max_length=20)
    is_guest = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    profile_picture = models.ForeignKey(ProfilePictures, on_delete=models.SET_NULL, null=True, blank=True)
    own_profile_pictures = models.ManyToManyField(ProfilePictures, default=None, symmetrical=False, related_name='own_profile_pictures', blank=True)

    accept_friend_request = models.BooleanField(default=True)

    is_online = models.BooleanField(default=True)
    game_playing = models.CharField(max_length=5, default=None, null=True)
    last_online = models.DateTimeField(auto_now_add=True)

    coins = models.IntegerField(default=100)
    trophy = models.IntegerField(default=0)
    current_rank = models.IntegerField(default=None, null=True)
    highest_rank = models.IntegerField(default=None, null=True)

    def __str__(self):
        return f'{self.id} {self.username}'
