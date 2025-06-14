from django.db import models

from users.models import Users


class FriendRequests(models.Model):
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='friend_requests_sent')
    receiver = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='friend_requests_received')
    send_at = models.DateTimeField(auto_now_add=True)
    new = models.BooleanField(default=True)

    class Meta:
        unique_together = ('sender', 'receiver')
