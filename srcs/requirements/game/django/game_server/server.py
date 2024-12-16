from aiohttp import web
from game_server import io_handlers
from game_server import requests_handlers
from game_server.match import fetch_match
from game_server.match import Player, fetch_matches
from game_server.pong_game import Game
from game_server.pong_position import Position
from threading import Lock, Thread
from typing import Dict
import logging
import asyncio
import socketio
import time


class Server:
    sio: socketio.AsyncServer
    app: web.Application
    clients: Dict[str, Player] = {}
    games: Dict[int, Game] = {}
    games_lock: Lock
    loop: asyncio.AbstractEventLoop

    @staticmethod
    def serve():
        Server.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*', logger=False)
        Server.app = web.Application()
        Server.loop = asyncio.get_event_loop()
        Server.app.add_routes([web.post('/create-game', requests_handlers.create_game)])
        Server.sio.attach(Server.app, socketio_path='/ws/') #TODO -> change with '/ws/game/'
        Server.sio.on('connect', handler=io_handlers.connect)
        Server.sio.on('disconnect', handler=io_handlers.disconnect)
        Server.sio.on('get_games', handler=io_handlers.send_games)
        Server.sio.on('move_down', handler=io_handlers.move_down)
        Server.sio.on('move_up', handler=io_handlers.move_up)
        Server.sio.on('stop_moving', handler=io_handlers.stop_moving)
        Server.games_lock = Lock()
        port=5500
        logging.info(f"SocketIO server running on port {port}")
        # print(f"SocketIO server running on port {port}", flush=True)
        Server.launch_monitoring()
        web.run_app(Server.app, host='0.0.0.0', port=port, loop=Server.loop)

    @staticmethod
    def launch_game(match_code):
        time.sleep(1)
        match = fetch_match(match_code)
        print('launching game with : ')
        for team in match.teams:
            for player in team.players:
                print(player.user_id, flush=True)
        game = Game(Server.sio, match, Position(800, 600))
        print(Server.games_lock, flush=True)
        Server.games_lock.acquire()
        print(match_code, flush=True)
        Server.games[match_code] = game
        Server.games_lock.release()
        asyncio.run(Server.games[match_code].launch())

    @staticmethod
    def monitoring_routine():
        log = False
        # setting all matches in DB as finished
        #print(Server.games_lock, flush=True)
        matches = fetch_matches()
        for match in matches:
            if match.finished == False:
                match.finish_match()
        while True:
            Server.games_lock.acquire()
            try:
                for match_code, game in Server.games.items():
                    if game.check_zombie() == True:
                        Server.games.pop(match_code)
            except RuntimeError:
                Server.games_lock.release()
            Server.games_lock.release()
            time.sleep(0.1)
            # Flush stdout to print help aiohttp print its things
            if log == False:
                print('', flush=True)
                log = True

    @staticmethod
    def launch_monitoring():
        Thread(target=Server.monitoring_routine).start()

    @staticmethod
    def get_player_and_match_code(id: int):
        #print(Server.games_lock, flush=True)
        # await asyncio.sleep(1)
        Server.games_lock.acquire()
        for match_code in Server.games:
            print('la1', flush=True)
            for team in Server.games[match_code].match.teams:
                print('la2', flush=True)
                for player in team.players:
                    print(player.user_id, flush=True)
                    if player.user_id == id:
                        Server.games_lock.release()
                        return player, match_code
        Server.games_lock.release()
        raise Exception(f'No player with id {id} is awaited on this server')
