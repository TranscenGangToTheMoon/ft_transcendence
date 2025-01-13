from typing import Literal

from django.db import models
from lib_transcendence import endpoints
from lib_transcendence.services import request_chat, request_matchmaking
from rest_framework.exceptions import APIException

from users.models import Users


class BlockedUsers(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='blocked')
    blocked = models.ForeignKey(Users, on_delete=models.CASCADE)
    blocked_at = models.DateTimeField(auto_now_add=True)

    def blocked_services(self, status: Literal['block', 'unblock'] = 'block'):
        endpoint = endpoints.UsersManagement.fblocked_user.format(user_id=self.user_id, blocked_user_id=self.blocked_id)

        try:
            request_chat(endpoint=endpoint, method='PUT', data={'blocked': status == 'block'})
        except APIException:
            pass

        try:
            if status == 'block':
                method = 'POST'
            else:
                method = 'DELETE'
            request_matchmaking(endpoint=endpoint, method=method)
        except APIException:
            pass
