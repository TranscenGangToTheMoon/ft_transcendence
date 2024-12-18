from aiohttp import web
from game_server import io_handlers
from game_server import requests_handlers
from game_server.match import fetch_match
from game_server.match import Player, fetch_matches, finish_match
from game_server.pong_game import Game
from game_server.pong_position import Position
from threading import Lock, Thread
from typing import Dict
import logging
import asyncio
import socketio
import time


class Server:
    _sio: socketio.AsyncServer
    _app: web.Application
    _clients: Dict[str, Player] = {}
    _games: Dict[int, Game] = {}
    _games_lock: Lock
    _loop_lock: Lock
    _sio_lock: Lock
    _loop: asyncio.AbstractEventLoop

    @staticmethod
    def serve():
        Server._sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*', logger=False)
        Server._app = web.Application()
        Server._loop = asyncio.get_event_loop()
        Server._app.add_routes([web.post('/create-game', requests_handlers.create_game)])
        Server._sio.attach(Server._app, socketio_path='/ws/') #TODO -> change with '/ws/game/'
        Server._sio.on('connect', handler=io_handlers.connect)
        Server._sio.on('disconnect', handler=io_handlers.disconnect)
        Server._sio.on('get_games', handler=io_handlers.send_games)
        Server._sio.on('move_down', handler=io_handlers.move_down)
        Server._sio.on('move_up', handler=io_handlers.move_up)
        Server._sio.on('stop_moving', handler=io_handlers.stop_moving)
        Server._games_lock = Lock()
        Server._loop_lock = Lock()
        Server._sio_lock = Lock()
        port=5500
        logging.info(f"SocketIO server running on port {port}")
        # print(f"SocketIO server running on port {port}", flush=True)
        Server.launch_monitoring()
        web.run_app(Server._app, host='0.0.0.0', port=port, loop=Server._loop)

    @staticmethod
    def launch_game(match_code):
        time.sleep(1)
        match = fetch_match(match_code)
        print('launching game with : ')
        for team in match.teams:
            for player in team.players:
                print(player.user_id, flush=True)
        game = Game(Server._sio, match, Position(800, 600))
        print(Server._games_lock, flush=True)
        Server._games_lock.acquire()
        Server._games.pop(match_id)
        Server._games_lock.release()
        Server._games[match_code].launch()

    @staticmethod
    def emit(event: str, data=None, room=None, to=None, skip_sid=None):
        Server._loop_lock.acquire()
        Server._loop.call_soon_threadsafe(asyncio.create_task, Server._sio.emit(event, data=data, room=room, to=to, skip_sid=skip_sid))
        Server._loop_lock.release()

    @staticmethod
    def monitoring_routine():
        log = False
        '''setting all matches in DB as finished'''
        matches = fetch_matches()
        for match in matches:
            if match.finished == False:
                match.finish_match()
        while True:
            Server._games_lock.acquire()
            try:
                to_pop = []
                for match_code, game in Server._games.items():
                    if game.check_zombie() == True:
                        to_pop.append(match_code)
                        print(f'match {match_code} has been popped of the server', flush=True)
                for match_code in to_pop:
                    Server._games.pop(match_code)
            except RuntimeError:
                pass
            Server._games_lock.release()
            time.sleep(0.1)
            # Flush stdout to print help aiohttp print its things
            if log == False:
                print('', flush=True)
                log = True

    @staticmethod
    def launch_monitoring():
        Thread(target=Server.monitoring_routine).start()

    @staticmethod
    def delete_game(match_id):
        # TODO -> set game as finished (django endpoint)
        Server._games_lock.acquire()
        Server._games.pop(match_id)
        Server._games_lock.release()

    @staticmethod
    def get_player_and_match_id(user_id: int):
        Server._games_lock.acquire()
        for match_id in Server._games:
            for team in Server._games[match_id].match.teams:
                for player in team.players:
                    print(player.user_id, flush=True)
                    if player.user_id == id:
                        Server._games_lock.release()
                        return player, match_id
        Server._games_lock.release()
        raise Exception(f'No player with id {user_id} is awaited on this server')
