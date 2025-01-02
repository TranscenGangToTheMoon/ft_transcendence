from django.db import models


class Banned(models.Model):
    code = models.CharField(max_length=4, editable=False)
    banned_user_id = models.IntegerField()

    def __str__(self):
        return f'{self.banned_user_id} banned in {self.code}'


def delete_banned(code: str):
    Banned.objects.filter(code=code).delete()
