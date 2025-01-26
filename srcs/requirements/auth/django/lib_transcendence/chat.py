from lib_transcendence.validate_type import validate_type, surchage_list
from lib_transcendence import endpoints
from lib_transcendence.request import request_service


class AcceptChat:
    NONE = 'none'
    FRIENDS_ONLY = 'friends_only'
    EVERYONE = 'everyone'

    @staticmethod
    def validate(chat_status):
        return validate_type(chat_status, AcceptChat)

    @staticmethod
    def is_accept(accept_chat, is_friend):
        return accept_chat == AcceptChat.EVERYONE or (accept_chat == AcceptChat.FRIENDS_ONLY and is_friend)

    @staticmethod
    def attr():
        return surchage_list(AcceptChat)

    def __str__(self):
        return 'Chat status'


def post_messages(chat_id: int, content: str, token: str):
    return request_service('chat', endpoints.Chat.fmessage.format(chat_id=chat_id), 'POST', {'content': content}, token)
