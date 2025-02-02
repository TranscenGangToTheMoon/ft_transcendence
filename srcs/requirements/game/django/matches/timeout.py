import os
import time

from lib_transcendence.game import FinishReason
from matches.models import Matches


def check_timeout(match_id):
    time.sleep(int(os.environ['GAME_PLAYER_CONNECT_TIMEOUT']))
    try:
        match = Matches.objects.get(id=match_id)
        if not match.game_start:
            match.finish(FinishReason.PLAYERS_TIMEOUT)
    except Matches.DoesNotExist:
        pass
