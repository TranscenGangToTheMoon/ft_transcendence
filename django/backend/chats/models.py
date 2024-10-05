from datetime import datetime

from django.db import models
from django.dispatch import receiver

from users.models import Users


# Create your models here.
class Chats(models.Model):
    participants = models.ManyToManyField(Users)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20) # todo: we do that ?


class Messages(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE)
    author = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    send_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)
    # is_invite_request = models.BooleanField(default=False) todo handle

    @property
    def is_read(self):
        return self.read_at is not None

    def mark_as_read(self):
        self.read_at = datetime.now()
        self.save()


# Signal to check if both users are deleted
@receiver(models.signals.post_delete, sender=Users)
def delete_chat_if_both_users_deleted(sender, instance, **kwargs):
    print("coucou")
    # Get all chats instances involving the deleted users
    user_chats = instance.chats_set.all()

    for user_chat in user_chats:
        print(user_chat)
        chat = user_chat.chat

        if not chat.participants.exists():
            chat.delete()
            chat.save() # todo doesnt work
