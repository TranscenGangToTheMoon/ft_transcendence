from django.db import models


class Chats(models.Model):
    type = models.CharField(max_length=20)
    blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class ChatParticipants(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE, related_name='participants')
    user_id = models.IntegerField()
    username = models.CharField(max_length=50)
    view_chat = models.BooleanField(default=True)

    def __str__(self):
        return f'[{self.chat.id}] {self.user_id} {self.username}'
