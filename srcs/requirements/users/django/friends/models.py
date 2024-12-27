from django.db import models

from users.models import Users


class Friends(models.Model):
    friends = models.ManyToManyField(Users, symmetrical=False)
    friends_since = models.DateTimeField(auto_now_add=True)
    matches_play_against = models.PositiveIntegerField(default=0)
    user1_win = models.PositiveIntegerField(default=0)  # todo remake
    matches_played_together = models.PositiveIntegerField(default=0)
    matches_won_together = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def play_against(self, winner: Users):
        if winner.id == self.user1_win:
            self.user1_win += 1
        self.matches_play_against += 1
        self.save()

    def play_together(self, win: bool):
        if win:
            self.matches_won_together += 1
        self.matches_played_together += 1
        self.save()

    def __str__(self):
        return f'{self.id} {" - ".join([user.username for user in self.friends.all()])}'
