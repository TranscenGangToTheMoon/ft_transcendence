import asyncio
import socketio
from pong_position import Position
from pong_game import Game
from match import Match, Player
from aiohttp import web
import time
import os


class Server:
    sio: socketio.AsyncServer
    async def serve(self, app: web.Application, sio: socketio.AsyncServer):
        self.sio = sio
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

    def get_player(self, user_id: int) -> Player:
        for team in self.match.teams:
            for player in team.players:
                if player.user_id == user_id:
                    return player
        raise Exception(f'cannot find player with user_id {user_id}')

    async def wait_for_players(self, timeout: int):
        start_waiting = time.time()
        for team in self.match.teams:
            for player in team.players:
                while player.socket_id == -1:
                    if time.time() - start_waiting > timeout:
                        raise Exception(f'player socketio connection timed out : player_id: {player.user_id}')
                    await asyncio.sleep(1)

    async def init_game(self, match: Match):
        self.match:Match = match
        async def connect(sid, environ, auth):
            #TODO -> decode auth argument and get token + user_id
            # use that and handle errors
            # json_data = auth_verify(request.headers.get('Authorization'))
            #TODO -> rewrite with auth tokens
            user_id = '1'
            try:
                player = self.get_player(int(user_id))
                player.socket_id = sid
            except Exception:
                raise Exception('player trying to connect is not registered in any team')
        self.sio.on('connect', handler=connect)
        try:
            canvas_size_x = int(os.environ['CANVAS_SIZE_X'])
            canvas_size_y = int(os.environ['CANVAS_SIZE_Y'])
        except KeyError:
            canvas_size_x = 800
            canvas_size_y = 600
        self.canvas = Position(canvas_size_x, canvas_size_y)
        self.game = Game(self.match.teams, self.canvas)
        async def move_up(sid):
            self.game.get_racket(sid).move_up()
        self.sio.on('move_up', handler=move_up)
        async def move_down(sid):
            self.game.get_racket(sid).move_down()
        self.sio.on('move_down', handler=move_down)
        async def stop_moving(sid):
            self.game.get_racket(sid).stop_moving()
        self.sio.on('stop_moving', handler=stop_moving)
        try:
            timeout = int(os.environ['GAME_PLAYER_CONNECT_TIMEOUT'])
        except KeyError:
            timeout = 60
        await self.wait_for_players(timeout)

    # def launch_game(self):
    #     game_start_time = time.time()
    #     while True:
    #         frame_start_time = time.time()
    #         self.game.update()
    #         while (frame_start_time - time.time())
    #             asyncio.sleep(0,01)

    async def stop(self):
        await self.app.cleanup()
        await self.app.shutdown()
