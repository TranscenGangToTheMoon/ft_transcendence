from aiohttp.web_routedef import AbstractRouteDef
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
    def __init__(self, model, match_id):
        self.match_id = match_id
        self.racket: Racket
        self.model = model
        self.user_id = self.model.user_id
        self.socket_id = ''
        self.game = None

class Team():
    def __init__(self, model, match_id):
        self.match_id = match_id
        self.players: List[Player] = []
        self.model = model
        raw_players = self.model.players.all()
        for player in raw_players:
            self.players.append(Player(player, self.match_id, self))

class Match():
    def __init__(self, match_id):
        self.model = Matches.objects.get(id=match_id)
        self.id = match_id
        self.teams: List[Team] = []
        self.game_mode = self.model.game_mode
        raw_teams = self.model.teams.all()
        for team in raw_teams:
            self.teams.append(Team(team, self.id))

    def __str__(self):
        return self.model.id + ' ' + str(self.teams[0].model.players.all()) + ' ' + \
        str(self.teams[1].model.players.all())

def fetch_match(match_id):
    #print(f'fetching match {match_id}', flush=True)
    match = Match(match_id)
    #print(str(match))
    return match

async def fetch_match_async(match_id):
    return await sync_to_async(fetch_match)(match_id)

def fetch_matches():
    matches = Matches.objects.all()
    return matches

async def finish_match(match):
    return await sync_to_async(match.model.finish_match)()
