from typing import Literal

from lib_transcendence import endpoints
from lib_transcendence.game import GameMode
from lib_transcendence.services import request_game


def create_match(game_mode: Literal['duel', 'clash', 'ranked', 'custom_game'] | dict, team_a: int | list[int], team_b: int | list[int]):
    if type(team_a) is int:
        team_a = [team_a]
    if type(team_b) is int:
        team_b = [team_b]
    data = {'teams': {'a': team_a, 'b': team_b}}

    if type(game_mode) is dict:
        data.update(game_mode)
        data['game_mode'] = GameMode.TOURNAMENT
    else:
        data['game_mode'] = game_mode

    return request_game(endpoints.Game.create_match, method='POST', data=data)


def create_tournament_match(tournament_id, stage_id, n, player1, player2):
    data = {
        'tournament_id': tournament_id,
        'tournament_stage_id': stage_id,
        'tournament_n': n,
    }
    return create_match(data, player1, player2)
