from asgiref.sync import sync_to_async
from pong_player import Player, Team
from typing import List
import django
import os
import sys

# Django ORM setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game.settings')
django.setup()
from matches.models import Matches

# Init of global list of players
players: List[Player] = []

def make_teams(match_code):
    global players
    teams = []
    team_players = []
    match = Matches.objects.get(code=match_code)
    raw_teams = match.teams.all()
    for team in raw_teams:
        raw_players = team.players.all()
        for player in raw_players:
            players.append(Player(player.user_id))
            team_players.append(Player(player.user_id))
        teams.append(Team(team.id, team_players))
    return teams, match.game_mode

async def get_match(match_id):
    for i in range(0, 3):
        try:
            teams, game_mode = await sync_to_async(make_teams)(match_id)
            return teams, game_mode
        except Exception:
            pass
    return None, None
