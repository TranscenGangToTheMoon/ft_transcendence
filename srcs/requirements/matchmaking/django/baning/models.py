from django.db import models


class Baned(models.Model):
    code = models.CharField(max_length=4, editable=False)
    baned_user_id = models.IntegerField()

    def __str__(self):
        return f'{self.baned_user_id} baned in {self.code}'


def delete_baned(code: str):
    Baned.objects.filter(code=code).delete()
