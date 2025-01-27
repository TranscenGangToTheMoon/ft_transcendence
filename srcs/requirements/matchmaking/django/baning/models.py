from django.db import models


class Banned(models.Model):
    code = models.CharField(max_length=4)
    banned_user_id = models.IntegerField()


def delete_banned(code: str):
    Banned.objects.filter(code=code).delete()
