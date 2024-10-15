from django.db import models

from friends.models import Friends
from users.models import Users


class FriendRequests(models.Model):
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='received_friend_requests')
    send_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f'{self.sender.username} -> {self.receiver.username}'
