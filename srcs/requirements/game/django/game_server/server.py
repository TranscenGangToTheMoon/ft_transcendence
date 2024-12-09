from aiohttp import web
from game_server.match import fetch_match_async
from game_server.pong_game import Game
from game_server.pong_position import Position
from game_server.match import Player, fetch_matches
from threading import Lock, Thread
from typing import Dict
import time
import asyncio
import socketio

class Server:
    sio: socketio.AsyncServer
    def __init__(self):
        self.games: Dict[int, Game] = {}
        self.games_lock = Lock()

    def serve(self, app: web.Application, sio: socketio.AsyncServer, port: int):
        Server.sio = sio
        Server.app = app
        self.players: Dict[str, Player] = {}
        print(f"SocketIO server running on port {port}", flush=True)
        self.launch_monitoring()
        web.run_app(Server.app, host='0.0.0.0', port=port)

    async def launch_game(self, match_code):
        await asyncio.sleep(1)
        match = await fetch_match_async(match_code)
        print('launching game with : ')
        for team in match.teams:
            for player in team.players:
                print(player.user_id, flush=True)
        game = Game(Server.sio, match, Position(800, 600))
        print(self.games_lock, flush=True)
        self.games_lock.acquire()
        self.games[match_code] = game
        self.games_lock.release()
        Thread(target=self.games[match_code].launch).start()

    def monitoring_routine(self):
        # setting all matches in DB as finished
        print(self.games_lock, flush=True)
        matches = fetch_matches()
        for match in matches:
            if match.finished == False:
                match.finish_match()
        while True:
            self.games_lock.acquire()
            try:
                for match_code, game in self.games.items():
                    if game.check_zombie() == True:
                        self.games.pop(match_code)
            except RuntimeError:
                print(self.games_lock)
            self.games_lock.release()
            time.sleep(35)

    def launch_monitoring(self):
        Thread(target=self.monitoring_routine).start()

    def get_player_and_match_code(self, id: int):
        self.games_lock.acquire()
        for match_code in self.games:
            for team in self.games[match_code].match.teams:
                for player in team.players:
                    if player.user_id == id:
                        return player, match_code
        self.games_lock.release()
        raise Exception(f'No player with id {id} is awaited on this server')
