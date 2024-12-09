from datetime import datetime

from django.db import models

from chats.models import Chats, ChatParticipants


class Messages(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE, related_name='messages')
    author = models.IntegerField()
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)

    @property
    def is_read(self):
        return self.read_at is not None

    def mark_as_read(self):
        self.read_at = datetime.now()
        self.save()

    def __str__(self):
        return f'{self.author}: {self.content}'
