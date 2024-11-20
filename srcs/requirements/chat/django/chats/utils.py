from typing import Literal

from chats.models import Chats


def get_chat_together(user1, user2, field: Literal['user_id', 'username'] = 'username'):
    kwars_user1 = {f'participants__{field}': user1}
    kwars_user2 = {f'participants__{field}': user2}

    try:
        return Chats.objects.filter(**kwars_user1).get(**kwars_user2)
    except Chats.DoesNotExist:
        return None
