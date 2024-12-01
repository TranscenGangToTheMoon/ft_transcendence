from django.db import models


class Players(models.Model):
    user_id = models.IntegerField(unique=True)
    trophies = models.IntegerField()
    game_mode = models.CharField(max_length=10) # todo try to set available option right here (not in serializer)
    join_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user_id)
