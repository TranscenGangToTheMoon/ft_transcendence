from typing import Literal

from rest_framework.exceptions import APIException

from lib_transcendence import endpoints
from lib_transcendence.game import GameMode
from lib_transcendence.services import request_game


def create_match(game_mode: Literal['duel', 'clash', 'ranked', 'custom_game'] | str | dict, team_a: int | list[int] | dict, team_b: int | list[int] | dict):
    if type(team_a) is list:
        team_a = [{'id': u} for u in team_a]
    if type(team_b) is list:
        team_b = [{'id': u} for u in team_b]
    if type(team_a) is dict:
        team_a = [team_a]
    if type(team_b) is dict:
        team_b = [team_b]
    if type(team_a) is int:
        team_a = [{'id': team_a}]
    if type(team_b) is int:
        team_b = [{'id': team_b}]
    data = {'teams': {'a': team_a, 'b': team_b}}

    if type(game_mode) is dict:
        data.update(game_mode)
        data['game_mode'] = GameMode.TOURNAMENT
    else:
        data['game_mode'] = game_mode

    try:
        return request_game(endpoints.Game.create_match, method='POST', data=data)
    except APIException:
        pass
