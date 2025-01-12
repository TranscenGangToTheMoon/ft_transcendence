from lib_transcendence.validate_type import validate_type


class GameMode: # TODO fguirama: change to enum
    duel = 'duel'
    clash = 'clash'
    ranked = 'ranked'
    tournament = 'tournament'
    custom_game = 'custom_game'
    global_ = 'global'

    modes = [duel, clash, ranked, tournament, custom_game]

    @staticmethod
    def validate(mode):
        return validate_type(mode, GameMode(), GameMode.modes)

    @staticmethod
    def validate_lobby(mode):
        return validate_type(mode, GameMode(), (GameMode.clash, GameMode.custom_game))

    @staticmethod
    def tournament_field(game_mode):
        return game_mode in [GameMode.tournament, GameMode.global_]

    @staticmethod
    def own_goal_field(game_mode):
        return game_mode in [GameMode.clash, GameMode.global_]

    def __str__(self):
        return 'Game mode'


class Reason: # TODO fguirama: rename
    normal_end = 'normal-end'
    player_abandon = 'player-abandon'
    player_disconnect = 'player-disconnect'
    player_not_connected = 'player-not-connected'

    error_reasons = [player_abandon, player_disconnect, player_not_connected]
    reasons = [normal_end] + error_reasons

    @staticmethod
    def validate(mode):
        return validate_type(mode, Reason(), Reason.reasons)

    @staticmethod
    def validate_error(mode):
        return validate_type(mode, Reason(), Reason.error_reasons)

    def __str__(self):
        return 'Reason'
