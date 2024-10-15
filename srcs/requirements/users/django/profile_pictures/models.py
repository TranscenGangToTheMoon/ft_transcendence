from django.db import models


class ProfilePictures(models.Model):
    name = models.CharField(max_length=20, unique=True, editable=False)
    url = models.FilePathField()
    small = models.FilePathField()
    medium = models.FilePathField()
    large = models.FilePathField()
