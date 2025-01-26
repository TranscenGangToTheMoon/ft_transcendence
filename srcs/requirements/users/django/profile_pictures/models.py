from django.db import models


class ProfilePictures(models.Model):
    user = models.ForeignKey('users.Users', on_delete=models.CASCADE, related_name='profile_pictures')
    name = models.CharField(max_length=30, unique=True, editable=False)
    unlock_reason = models.CharField(max_length=100)
    url = models.FilePathField()
    small = models.FilePathField()
    medium = models.FilePathField()
    large = models.FilePathField()
    is_unlocked = models.BooleanField(default=False)

    def unlock(self):
        self.is_unlocked = True
        self.save()
