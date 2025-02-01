from django.db import models


class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=15)
