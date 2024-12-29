from datetime import datetime

from django.db import models

from chats.models import Chats, ChatParticipants


class Messages(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE, related_name='messages')
    author = models.IntegerField()
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.author}: {self.content}'
