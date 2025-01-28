from rest_framework.exceptions import PermissionDenied

from chats.models import ChatParticipants
from lib_transcendence.exceptions import MessagesException


def get_chat_participants(chat_id, user_id, view_chat_required=True):
    kwargs = {'chat_id': chat_id, 'user__id': user_id, 'chat__blocked': False}
    if view_chat_required:
        kwargs['view_chat'] = True

    try:
        return ChatParticipants.objects.get(**kwargs)
    except ChatParticipants.DoesNotExist:
        raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG_TO_CHAT)
