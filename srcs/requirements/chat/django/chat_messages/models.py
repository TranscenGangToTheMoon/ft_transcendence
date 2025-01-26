from django.db import models

from chats.models import Chats
from user_management.models import Users


class Messages(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def read(self):
        self.is_read = True
        self.save()
