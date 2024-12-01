from django.db import models


class Blocked(models.Model):
    user_id = models.IntegerField()
    blocked_user_id = models.IntegerField()
