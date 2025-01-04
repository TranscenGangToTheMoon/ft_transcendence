from lib_transcendence.validate_type import validate_type


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


class Reason:
    abandon = 'abandon'
    server_crash = 'server_crash'
    victory = 'victory'

    reasons = [abandon, server_crash, victory]

    @staticmethod
    def validate(mode):
        return validate_type(mode, Reason(), Reason.reasons)

    def __str__(self):
        return 'Reason'
