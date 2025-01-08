from lib_transcendence.validate_type import validate_type
from lib_transcendence.endpoints import Chat as endpoint
from lib_transcendence.request import request_service

class ChatType:
    private_message = 'private_message'
    lobby = 'lobby'
    tournament = 'tournament'
    custom_game = 'custom_game'

    types = [private_message, lobby, tournament, custom_game]

    @staticmethod
    def validate(chat_type):
        return validate_type(chat_type, ChatType(), ChatType.types)

    def __str__(self):
        return 'Chat type'


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
    return request_service('chat', endpoint.fmessage.format(chat_id=chat_id), 'POST', {'content': content}, token)
