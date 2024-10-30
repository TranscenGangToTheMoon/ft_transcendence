from utils import validate_type


class ChatType:
    private_message = 'private_message'
    team = 'team'
    tournament = 'tournament'
    custom_game = 'custom_game'

    types = [private_message, team, tournament, custom_game]

    @staticmethod
    def validate(chat_type):
        return validate_type(chat_type, ChatType, ChatType.types)

    def __str__(self):
        return 'Chat type'
