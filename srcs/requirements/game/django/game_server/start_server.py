from aiohttp import web
from pong_player import Player, Team
from server import Server
from typing import List
import asyncio
import os
import socketio
import sys
import time
import django
from asgiref.sync import sync_to_async


sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)
players: List[Player]

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game.settings')
django.setup()
from matches.models import Matches


@sio.event
def connect(sid, environ, auth):
    pass


@sio.event
async def chat_message(sid, data):
    print("message ", data)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


def get_ports():
    try:
        port = int(os.environ['GAME_SERVER_MIN_PORT'])
        max_port = int(os.environ['GAME_SERVER_MAX_PORT'])
    except KeyError:
        port = 5500
        max_port = 5700
    return (port, max_port)


def make_teams(match_code):
    teams = []
    players_list = []
    match = Matches.objects.get(code=match_code)
    raw_teams = match.teams.all()
    for team in raw_teams:
        raw_players = team.players.all()
        for player in raw_players:
            players_list.append(Player(player.user_id))
        teams.append(Team(team.id, players_list))
    return teams, match.game_mode


async def main():
    try:
        match_id = int(sys.argv[1])
    except Exception:
        return 1
    port, max_port = get_ports()
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
    while True:
        time.sleep(1)
    # TODO -> make server.launch_game()

if __name__ == '__main__':
    asyncio.run(main())
