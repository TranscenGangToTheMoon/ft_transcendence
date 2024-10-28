from django.db import models


class Chats(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20)


class ChatParticipants(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE, related_name='participants')
    user_id = models.IntegerField()
    view_chat = models.BooleanField(default=True)
    join_at = models.DateTimeField(auto_now_add=True)
