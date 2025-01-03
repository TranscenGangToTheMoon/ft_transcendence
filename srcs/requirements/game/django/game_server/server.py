from aiohttp import web
from game_server import io_handlers
from game_server import requests_handlers
from game_server.match import fetch_match
from game_server.match import Player, fetch_matches, finish_match
from game_server.pong_game import Game
from game_server.pong_position import Position
from threading import Lock
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
    def clear_database():
        time.sleep(2)
        matches = fetch_matches()
        for match in matches:
            if match.finished == False:
                match.finish_match()

    @staticmethod
    def serve():
        Server._sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*', logger=False)
        Server._app = web.Application()
        Server._loop = asyncio.get_event_loop()
        Server._app.add_routes([web.post('/create-game', requests_handlers.create_game)])
        Server._sio.attach(Server._app, socketio_path='/ws/game/') #TODO -> change with '/ws/game/'
        Server._sio.on('connect', handler=io_handlers.connect)
        Server._sio.on('disconnect', handler=io_handlers.disconnect)
        Server._sio.on('move_down', handler=io_handlers.move_down)
        Server._sio.on('move_up', handler=io_handlers.move_up)
        Server._sio.on('stop_moving', handler=io_handlers.stop_moving)
        Server._games_lock = Lock()
        Server._loop_lock = Lock()
        Server._sio_lock = Lock()
        port = 5500
        '''setting all matches in DB as finished'''
        Server.clear_database()
        print(f"SocketIO server running on port {port}", flush=True)
        web.run_app(Server._app, host='0.0.0.0', port=port, loop=Server._loop)

    @staticmethod
    def delete_game(match_id) -> None:
        with Server._games_lock:
            if Server._games[match_id].match.model.finished == False:
                Server._games[match_id].finish()
            Server._games.pop(match_id)

    @staticmethod
    def push_game(match_id, game) -> None:
        with Server._games_lock:
            Server._games[match_id] = game

    @staticmethod
    def get_game(match_id) -> Game:
        with Server._games_lock:
            try:
                game = Server._games[match_id]
            except KeyError as e:
                raise e
            return game

    @staticmethod
    def launch_game(match_id):
        time.sleep(1)
        match = fetch_match(match_id)
        print('creating game', flush=True)
        print(match, flush=True)
        game = Game(Server._sio, match, Position(800, 600))
        Server.push_game(match_id, game)
        Server._games[match_id].launch()

    @staticmethod
    def emit(event: str, data=None, room=None, to=None, skip_sid=None):
        with Server._loop_lock:
            Server._loop.call_soon_threadsafe(asyncio.create_task, Server._sio.emit(event, data=data, room=room, to=to, skip_sid=skip_sid))

    @staticmethod
    def get_player_and_match_id(user_id: int):
        with Server._games_lock:
            for match_id in Server._games:
                for team in Server._games[match_id].match.teams:
                    for player in team.players:
                        if player.user_id == user_id:
                            return player, match_id
            raise Exception(f'No player with id {user_id} is awaited on this server')
