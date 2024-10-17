from django.db import models


class Chats(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20)


class ChatParticipants(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE)
    user_id = models.IntegerField() # todo send user delete
    username = models.CharField(max_length=20) # todo send user rename
    # todo option for delete chat only for one user
