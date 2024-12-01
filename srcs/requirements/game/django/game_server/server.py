from typing import Dict
import socketio
from game_server.pong_game import Game
from game_server.pong_position import Position
from game_server.match import fetch_match
from aiohttp import web
import os
import time

class Server:
    sio: socketio.AsyncServer
    games: Dict[int, Game] = {}
    async def serve(self, app: web.Application, sio: socketio.AsyncServer):
        self.sio = sio
        self.port = int(os.environ['GAME_SERVER_PORT'])
        self.app = app
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host='0.0.0.0', port=self.port)
        await site.start()
        print(f"SocketIO server running on port {self.port}")

    def launch_game(self, match_code):
        print(f'launching the game {match_code}', flush=True)
        print(f'fetching match {match_code}', flush=True)
        time.sleep(1)
        match = fetch_match(match_code)
        print(f'fetched match_code is {match.model.code}')
        print(str(match))
        game = Game(self.sio, match, Position(800, 600))
        self.games[match_code] = game
        print(f'in thread match_code: {match.model.code}', flush=True)
        self.games[match_code].launch()
        # Thread(target=self.games[match_code].launch).start()

    async def stop(self):
        await self.app.cleanup()
        await self.app.shutdown()
