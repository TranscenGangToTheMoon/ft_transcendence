from django.db import models


class ParticipantsPlace(models.Model):
    creator = None
    user_id = None

    @property
    def place(self):
        return None
