from __future__ import annotations

from datetime import datetime
from math import log2

from django.db import models
from django.dispatch import receiver


class State:
    lobby = "lobby"
    in_game = "in_game"
    ended = "ended"

    main_page = "main_page"
    ended_screen = "ended_screen"

# python manage.py makemigration 'app'
# python manage.py migrate 'app'

# ---------- STATIC TABLE ----------------------------- #
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



# Users.objects.first().chats_set.all()
# Chats.objects.last().participants.all().exists()
# ---------- USER ----------------------------- #
class Users(models.Model):
    # editable -----
    username = models.CharField(max_length=20)
    password = models.TextField()
    picture_profile = models.ForeignKey(PictureProfiles, on_delete=models.SET_NULL, null=True)
    accept_friend_request = models.BooleanField(default=True)

    # update -----
    is_online = models.BooleanField()
    last_online = models.DateTimeField()

    # static -----
    created_at = models.DateTimeField(auto_now_add=True)
    is_guest = models.BooleanField(default=False) # Guest79294

    # game -----
    trophy = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    title = models.ForeignKey(Titles, on_delete=models.SET_NULL, null=True)
    rank = models.ForeignKey(Ranks, on_delete=models.SET_NULL, null=True)

    # many to many -----
    friend_requests = models.ManyToManyField('self', through='FriendRequests')
    blocked_users = models.ManyToManyField('self', through='BlockedUsers')
    chats = models.ManyToManyField('self', through='Chats')

class FriendRequests(models.Model):
    user_from = models.ForeignKey(Users, on_delete=models.CASCADE)
    user_to = models.ForeignKey(Users, on_delete=models.CASCADE)
    send_at = models.DateTimeField(auto_now_add=True)

class BlockedUsers(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    user_blocked = models.ForeignKey(Users, on_delete=models.CASCADE)
    blocked_at = models.DateTimeField(auto_now_add=True)


# ---------- CHAT ----------------------------- #
class Chats(models.Model):
    participants = models.ManyToManyField(Users)
    created_at = models.DateTimeField(auto_now_add=True)

class Messages(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE)
    user_send = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    send_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)
    # is_invite_request = models.BooleanField(default=False) todo handle

    @property
    def is_read(self):
        return self.read_at is not None

    def mark_as_read(self):
        self.read_at = datetime.now()
        self.save()


# Signal to check if both users are deleted
@receiver(models.signals.post_delete, sender=Users)
def delete_chat_if_both_users_deleted(sender, instance, **kwargs):
    print("coucou")
    # Get all chat instances involving the deleted user
    user_chats = instance.chats_set.all()

    for user_chat in user_chats:
        print(user_chat)
        chat = user_chat.chat

        if not chat.participants.exists():
            chat.delete()
            chat.save() # todo doesnt work


# ---------- GAME ----------------------------- #
class Players(models.Model):
    user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True)
    ball_touched = models.IntegerField(default=0)
    score_points = models.IntegerField(default=0)
    most_use_spells = models.ForeignKey(Spells, on_delete=models.SET_NULL, null=True)

class Teams(models.Model):
    participants = models.ManyToManyField(Players)
    score = models.IntegerField()

    @property
    def players_count(self):
        return len(self.participants.all())

class Matches(models.Model):
    game_mode = models.ForeignKey(GameModes, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    teams = models.ManyToManyField(Teams)
    game_duration = models.DurationField()
    state = models.CharField(max_length=20, default=State.lobby) # "lobby" - "playing" - "ended"
    winner = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True)
    tournament = models.ForeignKey('Tournaments', on_delete=models.CASCADE, null=True, default=None)

# Tournaments ------
class Tournaments(models.Model):
    name = models.CharField(max_length=50)
    participants = models.ManyToManyField(Players)
    max_players = models.ForeignKey(MaxPlayersTournament, on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length=20, default=State.lobby) # "lobby" - "playing" - "ended"
    rounds = models.ManyToManyField(Matches)

    @property
    def current_round(self):
        return len(self.rounds.all())


# ---------- Stats ----------------------------- #
class Stats(models.Model):
    # todo: auto update when register new match
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    game_mode = models.ForeignKey(GameModes, on_delete=models.SET_NULL, null=True)
    score_points = models.IntegerField(default=0)
    cashed_points = models.IntegerField(default=0)
    game_played = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    longest_win_streak = models.IntegerField(default=0)


# ---------- SEASON ----------------------------- #
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
