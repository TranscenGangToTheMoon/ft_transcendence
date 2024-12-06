from django.db import models


class Blocked(models.Model):
    user_id = models.IntegerField()
    blocked_user_id = models.IntegerField()

    def __str__(self):
        return f'{self.user_id} blocked {self.blocked_user_id}'
