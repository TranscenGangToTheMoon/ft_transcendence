from django.db import models

from users.models import Users


class Blocks(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='block')
    blocked = models.ForeignKey(Users, on_delete=models.CASCADE)
    blocked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} {self.user} {self.blocked}'
