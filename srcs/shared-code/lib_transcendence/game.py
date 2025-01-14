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
    NORMAL_END = 'The game is over' # todo error
    PLAYER_ABANDON = 'A player has abandoned the game'
    PLAYER_DISCONNECT = 'A player has disconnected'
    PLAYER_NOT_CONNECTED = 'Not all players are connected'
    PLAYERS_TIMEOUT = 'Players have timed out'

    @staticmethod
    def validate(mode):
        return validate_type(mode, FinishReason)

    @staticmethod
    def validate_error(mode):
        return validate_type(mode, FinishReason, [FinishReason.PLAYER_ABANDON, FinishReason.PLAYER_NOT_CONNECTED])

    @staticmethod
    def attr():
        return surchage_list(FinishReason)

    def __str__(self):
        return 'Finish reason'
