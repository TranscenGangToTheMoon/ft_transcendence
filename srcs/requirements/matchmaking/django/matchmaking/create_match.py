from typing import Literal

from lib_transcendence import endpoints
from lib_transcendence.game import GameMode
from lib_transcendence.services import request_game


def create_match(game_mode: Literal['duel', 'clash', 'ranked', 'custom_game'] | dict, teams):
    data = {'teams': teams}

    if type(game_mode) is dict:
        data.update(game_mode)
        data['game_mode'] = GameMode.tournament
    else:
        data['game_mode'] = game_mode
        data['tournament_stage_id'] = None

    request_game(endpoints.Game.match, data=data)


def create_tournament_match(tournament_id, stage_id, teams):
    data = {
        'tournament_id': tournament_id,
        'tournament_stage_id': stage_id,
    }
    create_match(data, teams)
