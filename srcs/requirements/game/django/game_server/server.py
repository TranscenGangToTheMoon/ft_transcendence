from aiohttp import web
from game_server.match import fetch_match_async
from game_server.pong_game import Game
from game_server.pong_position import Position
from threading import Thread
from typing import Dict
import asyncio
import socketio

class Server:
    sio: socketio.AsyncServer
    games: Dict[int, Game] = {}
    def serve(self, app: web.Application, sio: socketio.AsyncServer, port: int):
        Server.sio = sio
        Server.app = app
        print(f"SocketIO server running on port {port}", flush=True)
        web.run_app(self.app, host='0.0.0.0', port=port)

    async def launch_game(self, match_code):
        await asyncio.sleep(1)
        print(f'creating game {match_code}', flush=True)
        # match = fetch_match(match_code)
        match = await fetch_match_async(match_code)
        game = Game(Server.sio, match, Position(800, 600))
        Server.games[match_code] = game
        print(f'creating game {match_code}', flush=True)
        Thread(target=Server.games[match_code].launch).start()

    async def stop(self):
        await self.app.cleanup()
        await self.app.shutdown()
