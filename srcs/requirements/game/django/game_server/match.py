from asgiref.sync import sync_to_async
from typing import List

# Django ORM setup
import os
import sys
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game.settings')
django.setup()
from matches.models import Matches, Teams, Players

class Player():
    model: Players
    socket_id: int
    user_id: int
    def __init__(self, model):
        self.model = model
        self.user_id = model.id
        self.socket_id = -1

class Team():
    model: Teams
    def __init__(self, model):
        self.players: List[Player] = []
        self.model = model
        raw_players = model.players.all()
        for player in raw_players:
            self.players.append(Player(player))

class Match():
    model: Matches
    game_mode: str = 'duel'
    viewers = List[Player]

    def __init__(self, match_code):
        self.model = Matches.objects.get(code=match_code)
        self.teams: List[Team] = []
        self.game_mode = self.model.game_mode
        raw_teams = self.model.teams.all()
        for team in raw_teams:
            self.teams.append(Team(team))

    def __str__(self):
        return self.model.code + ' ' + str(self.teams[0].model) + ' ' + str(self.teams[0].model.players.all())

def fetch_match(match_code):
    match = Match(match_code)
    print(str(match))
    return match
