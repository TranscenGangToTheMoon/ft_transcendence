from django.contrib.auth.models import User
from django.db import models

from games.models_static import Ranks, GameModes


# Create your models here.
class Titles(models.Model):
    name = models.CharField(max_length=70, unique=True, editable=False)


class ProfilePictures(models.Model):
    name = models.CharField(max_length=20, unique=True, editable=False)
    path = models.FilePathField()


class OnlineStatus(models.Model):
    name = models.CharField(max_length=30, unique=True, editable=False)


class Users(models.Model):
    # todo utils:
    # Users.objects.first().chats_set.all()
    # Chats.objects.last().participants.all().exists()
    username = models.CharField(max_length=40, null=True, unique=True, blank=True)#, validators=[validate_username])
    password = models.TextField(default=None, null=True, blank=True)
    django_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, default=None)
    profile_picture = models.ForeignKey(ProfilePictures, on_delete=models.SET_NULL, null=True, blank=True)
    own_profile_picture = models.ManyToManyField(ProfilePictures, default=None, symmetrical=False, related_name='own_profile_picture', blank=True)
    # point to default profile_picture
    accept_friend_request = models.BooleanField(default=True)

    blocked_users = models.ManyToManyField('self', default=None, symmetrical=False, blank=True)
    # friend_requests_sent = models.ManyToManyField('self', through='FriendRequests', symmetrical=False)
    # friends = models.ManyToManyField('self', through='Friends', symmetrical=True, related_name='friends_list')

    online_status = models.ForeignKey(OnlineStatus, default=None, on_delete=models.SET_NULL, null=True, blank=True)
    last_online = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_guest = models.BooleanField(default=True)

    trophy = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    title = models.ForeignKey(Titles, on_delete=models.SET_NULL, default=None, null=True, related_name='use_title', blank=True)
    own_titles = models.ManyToManyField(Titles, default=None, symmetrical=False, related_name='own_titles', blank=True)
    rank = models.ForeignKey(Ranks, default=None, on_delete=models.SET_NULL, null=True, blank=True)


class FriendRequests(models.Model):
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='received_friend_requests')
    send_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def accept(self):
        # friend_request = FriendRequest.objects.get(sender=sender, receiver=receiver)
        # friend_request.accept()

        self.sender.friends.add(self.receiver)

        self.delete()


class Friends(models.Model):
    # user1 is users that sent friends request
    user1 = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='friends_user1')
    user2 = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='friends_user2')
    # users = models.ManyToManyField(Users, symmetrical=True, related_name='friends_set')
    friends_since = models.DateTimeField(auto_now_add=True)
    matches_play_against = models.PositiveIntegerField(default=0)
    user1_win = models.PositiveIntegerField(default=0)
    matches_play_together = models.PositiveIntegerField(default=0)
    matches_win_together = models.PositiveIntegerField(default=0)

    def play_against(self, winner: Users):
        if winner.pk == self.user1_win:
            self.user1_win += 1
        self.matches_play_against += 1
        self.save()

    def play_together(self, win: bool):
        if win:
            self.matches_win_together += 1
        self.matches_play_together += 1
        self.save()

    class Meta:
        unique_together = ('user1', 'user2')


class Stats(models.Model):
    # todo: auto update when register new match
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    game_mode = models.ForeignKey(GameModes, on_delete=models.SET_NULL, null=True)
    score_points = models.IntegerField(default=0)
    cashed_points = models.IntegerField(default=0)
    game_played = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    longest_win_streak = models.IntegerField(default=0)
