from django.db import models

from users.models import Users


class FriendRequests(models.Model):
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='received_friend_requests')
    send_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def accept(self):
        friend = Friends.objects.create()
        friend.friends.add(self.sender, self.receiver)
        self.delete()

    def __str__(self):
        return f'{self.sender.username} sent to {self.receiver.username}'


class Friends(models.Model):
    friends = models.ManyToManyField(Users, symmetrical=False)
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

    def __str__(self):
        return f'{self.friends.all()}'
