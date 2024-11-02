from lib_transcendence.utils import validate_type


class GameMode:
    duel = 'duel'
    clash = 'clash'
    ranked = 'ranked'
    tournament = 'tournament'
    custom_game = 'custom_game'

    modes = [duel, clash, ranked, tournament, custom_game]

    @staticmethod
    def validate(mode):
        return validate_type(mode, GameMode(), GameMode.modes)

    @staticmethod
    def validate_lobby(mode):
        return validate_type(mode, GameMode(), (GameMode.clash, GameMode.custom_game))

    def __str__(self):
        return 'Game mode'
