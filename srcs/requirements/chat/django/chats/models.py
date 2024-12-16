from django.db import models


class Chats(models.Model):
    type = models.CharField(max_length=20)
    blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def update(self):
        self.last_updated = self.last_updated
        self.save()


class ChatParticipants(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE, related_name='participants')
    user_id = models.IntegerField()
    username = models.CharField(max_length=30)
    view_chat = models.BooleanField(default=True)

    def set_view_chat(self, view_chat=True):
        self.view_chat = view_chat
        self.save()

    def __str__(self):
        return f'[{self.chat.id}] {self.user_id} {self.username}'
