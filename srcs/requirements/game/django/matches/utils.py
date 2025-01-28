from rest_framework.exceptions import APIException

from lib_transcendence import endpoints
from lib_transcendence.exceptions import ServiceUnavailable
from lib_transcendence.services import request_users


def send_match_result(match):
    try:
        from matches.serializers import MatchSerializer

        request_users(endpoints.Users.result_match, 'POST', data=MatchSerializer(match, context={'retrieve_users': False}).data)
    except APIException:
        raise ServiceUnavailable('users')


def compute_trophies(winner_trophies, looser_trophies):
    gap = abs(winner_trophies - looser_trophies)
    win_trophies = 30 - (winner_trophies / 2000) * 10
    loose_trophies = 20 + (looser_trophies / 2000) * 15
    adjust_gap = gap / 10
    if winner_trophies > looser_trophies:
        adjust_gap *= -1
    looser_trophies -= adjust_gap
    if 1000 < winner_trophies <= looser_trophies:
        adjust_gap = adjust_gap / (winner_trophies / 1000)
    win_trophies += adjust_gap
    return round(win_trophies), round(loose_trophies)
