from typing import Literal

from rest_framework.exceptions import NotFound

from chats.models import Chats
from lib_transcendence.exceptions import MessagesException


def get_chat_together(user1, user2, field: Literal['user__id', 'user__username'] = 'user__username', raise_exception=False):
    kwars_user1 = {f'participants__{field}': user1}
    kwars_user2 = {f'participants__{field}': user2}

    try:
        return Chats.objects.filter(**kwars_user1).get(**kwars_user2)
    except Chats.DoesNotExist:
        if raise_exception:
            raise NotFound(MessagesException.NotFound.CHAT)
        return None
