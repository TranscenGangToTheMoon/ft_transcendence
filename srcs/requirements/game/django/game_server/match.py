from aiohttp.web_routedef import AbstractRouteDef
from typing import List

import requests
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
        self.csc = 0

class Team():
    def __init__(self, players, match_id, name):
        self.match_id = match_id
        self.players: List[Player] = []
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

def fetch_matches():
    print('fetching matches', flush=True)
    return Matches.objects.filter(finished=False)

def finish_match(match_id, reason=None):
    # todo -> change to use API when it's ready
    # r = requests.post(f'http://localhost:8000/matches/{match_id}/finish_match')
    match = Matches.objects.get(id=match_id)
    match.finish_match(reason)
