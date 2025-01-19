from lib_transcendence.validate_type import validate_type, surchage_list


class GameMode:
    DUEL = 'duel'
    CLASH = 'clash'
    RANKED = 'ranked'
    TOURNAMENT = 'tournament'
    CUSTOM_GAME = 'custom_game'
    GLOBAL = 'global'

    @staticmethod
    def validate(mode):
        return validate_type(mode, GameMode)

    @staticmethod
    def validate_lobby(mode):
        return validate_type(mode, GameMode, [GameMode.CLASH, GameMode.CUSTOM_GAME])

    @staticmethod
    def tournament_field(game_mode):
        return game_mode in [GameMode.TOURNAMENT, GameMode.GLOBAL]

    @staticmethod
    def own_goal_field(game_mode):
        return game_mode in [GameMode.CLASH, GameMode.GLOBAL]

    @staticmethod
    def attr():
        result = surchage_list(GameMode)
        result.remove(GameMode.GLOBAL)
        return result

    def __str__(self):
        return 'Game mode'


class FinishReason:
    NORMAL_END = 'normal-end'
    PLAYER_DISCONNECT = 'player-disconnect'
    PLAYER_NOT_CONNECTED = 'player-not-connected'
    PLAYERS_TIMEOUT = 'Players-timeout'
    GAME_NOT_PLAYED = 'game-not-played'
    NO_GAME = 'no-game'

    @staticmethod
    def validate(mode):
        return validate_type(mode, FinishReason)

    @staticmethod
    def validate_error(mode):
        return validate_type(mode, FinishReason, [FinishReason.PLAYER_DISCONNECT, FinishReason.PLAYER_NOT_CONNECTED])

    @staticmethod
    def attr():
        return surchage_list(FinishReason)

    def __str__(self):
        return 'Finish reason'
