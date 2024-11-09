from typing import Literal

from utils.credentials import new_user
from utils.request import make_request


def play(user=None, game_mode: Literal['ranked', 'duel'] = 'duel'):
    if user is None:
        user = new_user()
    return make_request(
        endpoint=f'play/{game_mode}/',
        method='POST',
        token=user['token'],
    )
