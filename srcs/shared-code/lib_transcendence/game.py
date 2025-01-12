from enum import Enum

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


class FinishReason:
    normal_end = 'normal-end'
    player_abandon = 'player-abandon'
    player_disconnect = 'player-disconnect'
    player_not_connected = 'player-not-connected'

    error_finish_reasons = [player_abandon, player_disconnect, player_not_connected]
    finish_reasons = [normal_end] + error_finish_reasons

    @staticmethod
    def validate(mode):
        return validate_type(mode, FinishReason(), FinishReason.finish_reasons)

    @staticmethod
    def validate_error(mode):
        return validate_type(mode, FinishReason(), FinishReason.error_finish_reasons)

    def __str__(self):
        return 'FinishReason'
