from django.db import models

from users.models import Users


class Friends(models.Model):
    user_1 = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='friend_1')
    user_2 = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='friend_2')
    friends_since = models.DateTimeField(auto_now_add=True)
    matches_play_against = models.PositiveIntegerField(default=0)
    user1_wins = models.PositiveIntegerField(default=0)
    user2_wins = models.PositiveIntegerField(default=0)
    matches_played_together = models.PositiveIntegerField(default=0)
    matches_won_together = models.PositiveIntegerField(default=0)

    def play_against(self, winner: Users):
        if winner == self.user_1:
            self.user1_wins += 1
        else:
            self.user2_wins += 1
        self.matches_play_against += 1
        self.save()

    def play_together(self, win: bool):
        if win:
            self.matches_won_together += 1
        self.matches_played_together += 1
        self.save()
