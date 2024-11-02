from chats.models import Chats


def get_chat_together(user1, user2):
    try:
        return Chats.objects.filter(participants__username__in=user1).get(participants__username__in=user2)
    except Chats.DoesNotExist:
        return None
