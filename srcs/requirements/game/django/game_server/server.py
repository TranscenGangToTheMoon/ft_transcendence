from typing import List
from lib_transcendence.game import GameMode
from aiohttp import web
import os


class Server:
    async def serve(self, app: web.Application):
        try:
            min_port = int(os.environ['GAME_SERVER_MIN_PORT'])
            max_port = int(os.environ['GAME_SERVER_MAX_PORT'])
        except KeyError:
            min_port = 5500
            max_port = 5700
        self.app = app
        self.running = False
        for port in range(min_port, max_port + 1):
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, 'localhost', port)
            try:
                await site.start()
                print(f"Port: {port}", flush=True)
                return
            except OSError:
                continue
        raise Exception('No port available')
        #TODO -> replace with real error message

    def init_game(self,
                  game_mode: str = GameMode.duel,
                  players: List[int] = []):
        self.players = players
        self.game_mode = game_mode

    async def stop(self):
        await self.app.cleanup()
        await self.app.shutdown()
