from typing import List
from lib_transcendence.game import GameMode
import socketio
from pong_position import Position
from pong_player import Player, Team
from pong_game import Game
from aiohttp import web
import time
import os


class Server:
    players: List[Player]
    async def serve(self, app: web.Application, sio: socketio.AsyncServer):
        async def connect(sid, environ, auth):
            user_id = await sio.emit('user_id')
            for team in self.teams:
                for player in team.players:
                    # if player.id == int(environ.get('userid')):
                    if player.id == user_id:
                        player.socket_id = sid
                    #TODO -> rewrite with auth tokens
        sio.on('connect', handler=connect)
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
            site = web.TCPSite(runner, host='0.0.0.0', port=port)
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
                  teams: List[Team] = []) -> bool:
        canvas = Position(800, 600)
        self.teams: List[Team] = teams
        if len(self.teams) != 2:
            raise Exception('teams count is not 2')
        self.game: Game = Game(self.teams[0], self.teams[1], canvas)
        self.game_mode: str = game_mode
        try:
            timeout = int(os.environ['GAME_PLAYER_CONNECT_TIMEOUT'])
        except Exception:
            timeout = 3
        for team in self.teams:
            for player in team.players:
                start_waiting = time.time()
                while player.socket_id == -1:
                    if time.time() - start_waiting > timeout:
                        return False
                    time.sleep(1)
        return True

    async def stop(self):
        await self.app.cleanup()
        await self.app.shutdown()
