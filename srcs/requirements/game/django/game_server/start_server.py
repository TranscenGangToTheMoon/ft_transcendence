from aiohttp import web
from asgiref.sync import sync_to_async
from pong_player import Player, Team
from server import Server
from typing import List
import asyncio
import django
# import json
import os
import socketio
from socket_init import init_socketIO
import sys
import time

# Django ORM setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game.settings')
django.setup()
from matches.models import Matches

# SocketIO setup
sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)
init_socketIO(sio)

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


async def main():
    try:
        match_id = int(sys.argv[1])
    except Exception:
        return 1
    server = Server()
    try:
        await server.serve(app)
    except Exception:
        return (1)
    got_request = False
    i = 0
    while not got_request and i < 3:
        try:
            teams, game_mode = await sync_to_async(make_teams)(match_id)
            got_request = True
        except Exception:
            i += 1
    if not got_request:
        return (1)
    server.init_game()
    while True:
       time.sleep(1)
    # server.launch_game()
    # TODO -> make server.launch_game()

if __name__ == '__main__':
    asyncio.run(main())
