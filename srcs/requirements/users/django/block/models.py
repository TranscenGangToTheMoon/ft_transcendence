from django.db import models

from users.models import Users


class Block(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    blocked = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='blocked_user')
    blocked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} {self.user} {self.blocked}'
