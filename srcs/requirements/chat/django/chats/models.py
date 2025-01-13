from django.db import models

from user_management.models import Users


class Chats(models.Model):
    blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def update(self):
        self.last_updated = self.last_updated
        self.save()


class ChatParticipants(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='chats')
    view_chat = models.BooleanField(default=True)

    def set_view_chat(self, view_chat=True):
        self.view_chat = view_chat
        self.save()
