from lib_transcendence import endpoints
from lib_transcendence.request import request_service
from lib_transcendence.validate_type import validate_type


class AcceptChat:
    none = 'none'
    friends_only = 'friends_only'
    everyone = 'everyone'

    accept = [none, friends_only, everyone]

    @staticmethod
    def validate(chat_status):
        return validate_type(chat_status, AcceptChat(), AcceptChat.accept)

    @staticmethod
    def is_accept(accept_chat, is_friend):
        return accept_chat == AcceptChat.everyone or (accept_chat == AcceptChat.friends_only and is_friend)

    def __str__(self):
        return 'Chat status'


def post_messages(chat_id: int, content: str, token: str):
    return request_service('chat', endpoints.Chat.fmessage.format(chat_id=chat_id), 'POST', {'content': content}, token)
