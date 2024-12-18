from asgiref.sync import sync_to_async
from typing import List
from game_server.pong_racket import Racket

# Django ORM setup
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game.settings')
django.setup()
from matches.models import Matches

class Player():
    def __init__(self, model, match_code):
        self.match_code = match_code
        self.racket = None
        self.model = model
        self.user_id = self.model.user_id
        self.socket_id = ''
        self.game = None

class Team():
    def __init__(self, model, match_code):
        self.match_code = match_code
        self.players: List[Player] = []
        self.model = model
        raw_players = self.model.players.all()
        for player in raw_players:
            self.players.append(Player(player, self.match_code))

class Match():
    def __init__(self, match_code):
        self.model = Matches.objects.get(code=match_code)
        self.code = self.model.code
        self.teams: List[Team] = []
        self.game_mode = self.model.game_mode
        raw_teams = self.model.teams.all()
        for team in raw_teams:
            self.teams.append(Team(team, self.code))

    def __str__(self):
        return self.model.code + ' ' + str(self.teams[0].model.players.all()) + ' ' + \
        str(self.teams[1].model.players.all())

def fetch_match(match_code):
    #print(f'fetching match {match_code}', flush=True)
    match = Match(match_code)
    #print(str(match))
    return match

async def fetch_match_async(match_code):
    return await sync_to_async(fetch_match)(match_code)

def fetch_matches():
    matches = Matches.objects.all()
    return matches

async def finish_match(match):
    return await sync_to_async(match.model.finish_match)()
