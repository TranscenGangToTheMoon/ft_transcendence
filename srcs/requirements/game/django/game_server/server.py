from aiohttp import web
from game_server import io_handlers
from game_server.match import Player
from game_server.game import Game
from game_server.pong_racket import Racket
from game_server.pong_position import Position
from threading import Lock, Thread
from typing import Dict
import logging
import asyncio
import socketio
import os
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
        Server._sio = socketio.AsyncServer(
            async_mode='aiohttp',
            cors_allowed_origins='*',
            logger=False,
            engineio_logger=False
        )
        Server._app = web.Application()
        Server._loop = asyncio.get_event_loop()
        Server._sio.attach(Server._app, socketio_path='/ws/game/')
        Server._sio.on('connect', handler=io_handlers.connect)
        Server._sio.on('disconnect', handler=io_handlers.disconnect)
        Server._sio.on('move_down', handler=io_handlers.move_down)
        Server._sio.on('move_up', handler=io_handlers.move_up)
        Server._sio.on('stop_moving', handler=io_handlers.stop_moving)
        Server._games_lock = Lock()
        Server._loop_lock = Lock()
        Server._sio_lock = Lock()
        try:
            Game.default_ball_speed = int(os.environ['GAME_DEFAULT_BALL_SPEED'])
            Game.ball_size = int(os.environ['GAME_BALL_SIZE'])
            Racket.width = int(os.environ['GAME_RACKET_WIDTH'])
            Racket.height = int(os.environ['GAME_RACKET_HEIGHT'])
            Racket.width_3v3 = int(os.environ['GAME_RACKET_WIDTH_3V3'])
            Racket.height_3v3 = int(os.environ['GAME_RACKET_HEIGHT_3V3'])
            Racket.max_speed = int(os.environ['GAME_RACKET_MAX_SPEED'])
        except KeyError:
            Game.default_ball_speed = 240
            Game.ball_size = 20
            Racket.width = 30
            Racket.height = 200
            Racket.width_3v3 = 30
            Racket.height_3v3 = 100
            Racket.max_speed = 500
        port = 5500
        print(f"SocketIO server running on port {port}", flush=True)
        web.run_app(Server._app, host='0.0.0.0', port=port, loop=Server._loop)

    class ServerException(Exception):
        pass

    @staticmethod
    def delete_game(match_id) -> None:
        with Server._games_lock:
            try:
                Server._games.pop(match_id)
                with Server._loop_lock:
                    Server._loop.call_soon_threadsafe(asyncio.create_task, Server._sio.close_room(str(match_id)))
            except KeyError:
                pass # game has already been deleted

    @staticmethod
    def finish_game(match_id, finish_reason: str, user_id: int | None = None) -> None:
        with Server._games_lock:
            game = Server._games[match_id]
        if game.finished is False:
            game.finish(finish_reason, disconnected_user_id=user_id)

    @staticmethod
    def push_game(match_id, game) -> None:
        with Server._games_lock:
            Server._games[match_id] = game

    @staticmethod
    def does_game_exist(match_id) -> bool:
        with Server._games_lock:
            return match_id in Server._games

    @staticmethod
    def create_game(match):
        game = Game(Server._sio, match)
        Server.push_game(match.id, game)
        Thread(target=Server._games[match.id].launch).start()

    @staticmethod
    def emit(event: str, data=None, room=None, to=None, skip_sid=None):
        if (room is None) and (to is None):
            raise Server.ServerException('Unauthorized: Emit to all clients is not allowed')
        with Server._loop_lock:
            Server._loop.call_soon_threadsafe(asyncio.create_task, Server._sio.emit(event, data=data, room=room, to=to, skip_sid=skip_sid))

    @staticmethod
    def disconnect(players=None, disconnected_sid=None, match_id: int | None = None):
        if players is None and match_id is None:
            raise Server.ServerException('No players or match_id provided')
        if players is None and match_id is not None:
            with Server._games_lock:
                players = Server._games[match_id].match.teams[0].players + Server._games[match_id].match.teams[1].players
        elif players is not None:
            for player in players:
                if player.socket_id == '':
                    continue
                Server._clients.pop(player.socket_id)
                if player.socket_id == disconnected_sid:
                    continue
                Server._loop.call_later(0.5, asyncio.create_task, Server._sio.disconnect(player.socket_id))
                player.socket_id = ''

    @staticmethod
    def get_player(user_id: int):
        with Server._games_lock:
            for match_id in Server._games:
                for team in Server._games[match_id].match.teams:
                    for player in team.players:
                        if player.user_id == user_id:
                            return player
        raise Exception(f'No player with id {user_id} is awaited on this server')
