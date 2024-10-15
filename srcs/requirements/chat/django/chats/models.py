from datetime import datetime

from django.db import models


class Chats(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20)


class ChatParticipants(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE)
    user_id = models.IntegerField() # todo delete
    username = models.CharField(max_length=20) # todo rename


class Messages(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE)
    author = models.IntegerField()
    content = models.TextField()
    send_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)

    @property
    def is_read(self):
        return self.read_at is not None

    def mark_as_read(self):
        self.read_at = datetime.now()
        self.save()
