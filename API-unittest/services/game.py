from typing import Literal

from utils.request import make_request


def create_game(user1, user2, game_mode: Literal['ranked', 'duel'] = 'duel', data=None, method: Literal['GET', 'POST', 'PATCH', 'DELETE'] = 'POST'):
    if data is None:
        data = {'game_mode': game_mode, 'teams': [[user1['id']], [user2['id']]]}
    return make_request(
        endpoint='match/',
        method=method,
        data=data,
        port=8003,
    )


def is_in_game(user1):
    return make_request(
        endpoint=f'match/{user1["id"]}/',
        port=8003,
    )
