from aiohttp.web_routedef import AbstractRouteDef
from typing import List
from lib_transcendence.request import AuthenticationFailed
from lib_transcendence.services import request_game
from lib_transcendence.game import Reason
from lib_transcendence import endpoints
from rest_framework.exceptions import APIException, NotFound
from game_server.pong_racket import Racket


import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game.settings')
django.setup()
from matches.models import Matches


class Player():
    def __init__(self, id, match_id, team):
        self.match_id = match_id
        self.racket: Racket
        self.user_id = id
        self.socket_id = ''
        self.game = None
        self.team = team
        self.score = 0
        self.csc = 0

    def score_goal(self, csc=False):
        try:
            request_game(endpoints.Game.fscore.format(user_id=self.user_id), 'POST', data={'own_goal': csc})
        except NotFound as e:
            print(e.detail, flush=True)
        except APIException as e:
            from game_server.server import Server
            Server.emit('disconnect', room=str(self.match_id))
        if csc:
            self.csc += 1
        else:
            self.score += 1
            self.team.score += 1


class Team():
    def __init__(self, players, match_id, name):
        self.match_id = match_id
        self.players: List[Player] = []
        self.name = name
        self.score = 0
        for player in players:
            self.players.append(Player(player['id'], match_id, self))


class Match():
    def __init__(self, game_data):
        self.id = game_data['id']
        self.teams: List[Team] = []
        self.game_mode = game_data['game_mode']
        teams = game_data['teams']
        for team_name, team in teams.items():
            self.teams.append(Team(team, self.id, team_name))


def finish_match(match_id, reason: str, user_id: int):
    if reason != Reason.normal_end:
        try:
            request_game(
                endpoints.Game.ffinish_match.format(match_id=match_id),
                'POST',
                data={
                    'reason': reason,
                    'id': user_id
                }
            )
        except AuthenticationFailed as e:
            print("The finish_match attribute is not available in the Game class.", flush=True)
        except Exception as e:
            print(f"An error occurred while requesting the game finish: {e}", flush=True)
