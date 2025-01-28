from django.db import models

from lib_transcendence.sse_events import EventCode
from profile_pictures.data import ProfilePicture


class ProfilePictures(models.Model):
    user = models.ForeignKey('users.Users', on_delete=models.CASCADE, related_name='profile_pictures')
    n = models.IntegerField()
    name = models.CharField(max_length=20)
    unlock_reason = models.CharField(max_length=40)
    url = models.CharField(max_length=70)
    small = models.CharField(max_length=70)
    medium = models.CharField(max_length=70)
    large = models.CharField(max_length=70)
    is_unlocked = models.BooleanField(default=False)
    is_equiped = models.BooleanField(default=False)

    def unlock(self):
        from profile_pictures.serializers import ProfilePicturesSerializer

        self.is_unlocked = True
        self.save()
        if self.name != ProfilePicture.DEFAULT:
            from sse.events import publish_event

            publish_event(self.user, EventCode.PROFILE_PICTURE_UNLOCKED, ProfilePicturesSerializer(self).data)

    def use(self, use=True):
        self.is_equiped = use
        self.save()
