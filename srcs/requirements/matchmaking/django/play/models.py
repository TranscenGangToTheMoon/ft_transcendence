from django.db import models


class Players(models.Model):
    user_id = models.IntegerField(unique=True)
    game_mode = models.CharField(max_length=50)
    join_at = models.DateTimeField(auto_now_add=True)
