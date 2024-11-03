from typing import Literal

from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated

from lib_transcendence.request import request_service


def requests_users(request, endpoint: Literal['users/me/', 'validate/chat/'], method: Literal['GET', 'PUT', 'PATCH', 'DELETE'], data=None):
    if request is None:
        raise serializers.ValidationError('Request is required.')
    token = request.headers.get('Authorization')
    if token is None:
        raise NotAuthenticated()

    return request_service('users', endpoint, method, data, token)


def requests_matchmaking(tournament_id, stage_id, winner, looser):
    data = {
        'tournament_id': tournament_id,
        'stage_id': stage_id,
        'winner': winner,
        'loser': looser,
    }

    return request_service('matchmaking', 'tournament/result-match/', 'POST', data)


def requests_game(endpoint: Literal['match/', 'tournaments/', 'playing/{user_id}/'], method: Literal['GET', 'POST'] = 'POST', data=None):
    return request_service('game', endpoint, method, data)


def requests_chat(endpoint: str, method: Literal['PATCH', 'DELETE'] = 'PATCH', data=None):
    return request_service('chat', endpoint, method, data)
