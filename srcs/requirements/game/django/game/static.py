import random
import string


class GameMode:
    duel = 'duel'
    clash = 'clash'
    ranked = 'ranked'
    tournament = 'tournament'
    custom_game = 'custom_game'

    @staticmethod
    def all():
        return [GameMode.duel, GameMode.clash, GameMode.ranked, GameMode.tournament, GameMode.custom_game]

    @staticmethod
    def str():
        return "'" + "', '".join(GameMode.all()[:-1]) + "' or '" + GameMode.all()[-1]


def generate_game_code():
    return ''.join(random.choices(string.digits, k=4))
