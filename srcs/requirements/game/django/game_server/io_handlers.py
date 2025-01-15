import asyncio
from typing import Any, Dict
from asgiref.sync import sync_to_async
from lib_transcendence.auth import auth_verify
from lib_transcendence.game import FinishReason
from logging import info, debug, error
from lib_transcendence.exceptions import MessagesException, ServiceUnavailable
from rest_framework.exceptions import NotFound
from lib_transcendence.services import request_game
from lib_transcendence import endpoints
from rest_framework.exceptions import APIException
from threading import Thread
from game_server.match import Match


# TODO -> change this to use the Server class
async def connect(sid, environ, auth):
    from game_server.server import Server
    print('trying to connect', flush=True)
    token = auth.get('token')
    if token is None:
        raise ConnectionRefusedError(MessagesException.Authentication.NOT_AUTHENTICATED)
    token = 'Bearer ' + token
    try:
        user_data = auth_verify(token)
    except APIException as e:
        raise ConnectionRefusedError(e.detail)
    if user_data is None:
        raise ConnectionRefusedError(MessagesException.Authentication.NOT_AUTHENTICATED)
    id = user_data['id']
    print(f'user_id = {id}', flush=True)
    try:
        game_data = request_game(endpoints.Game.fmatch_user.format(user_id=id), 'GET')
    except NotFound as e:
        raise ConnectionRefusedError(e.detail)
    except APIException as e:
        raise ConnectionRefusedError(MessagesException.ServiceUnavailable.game)
    if game_data is None:
        raise ConnectionRefusedError(MessagesException.ServiceUnavailable.game)
    print(f"game_data = {game_data}", flush=True)
    game_id = game_data['id']
    print(f"game_id = {game_id}", flush=True)
    if not Server.does_game_exist(game_id):
        match = Match(game_data)
        Server.create_game(match)
        # TODO -> request game to say the first player is connected
    player = Server.get_player(id)
    print(f"player = {player}")
    print(f"sid = {sid}", flush=True)
    player.socket_id = sid
    Server._clients[sid] = player
    await Server._sio.enter_room(sid, str(game_id))
    print(f'User {id} connected & authenticated', flush=True)


async def move_up(sid):
    from game_server.server import Server
    player = Server._clients[sid]
    await Server._sio.emit(
        'move_up',
        data={'player': player.user_id},
        room=str(player.match_id),
        skip_sid=sid)
    player.racket.move_up()


async def move_down(sid):
    from game_server.server import Server
    player = Server._clients[sid]
    await Server._sio.emit(
        'move_down',
        data={'player': player.user_id},
        room=str(player.match_id),
        skip_sid=sid
    )
    player.racket.move_down()


async def stop_moving(sid, data):
    from game_server.server import Server
    player = Server._clients[sid]
    try:
        position = data['position']
    except KeyError:
        error('Need position data for event stop_moving')
        await Server._sio.emit('error', data={'message': 'Need position data for event stop_moving'}, to=sid)
        return
    position = player.racket.stop_moving(position)
    await Server._sio.emit(
        'stop_moving',
        data={'player': player.user_id, 'position': position},
        room=str(player.match_id)
    )

# TODO -> make some tests for player abandon while a game is running
async def ff(sid):
    from game_server.server import Server
    try:
        match_id = Server._clients[sid].match_id
        await sync_to_async(Server.finish_game)(match_id, FinishReason.PLAYER_DISCONNECT, Server._clients[sid].user_id)
    except KeyError:
        pass


async def disconnect(sid):
    from game_server.server import Server
    try:
        match_id = Server._clients[sid].match_id
        await sync_to_async(Server.finish_game)(match_id, FinishReason.PLAYER_DISCONNECT, Server._clients[sid].user_id)
    except KeyError:
        pass # player has already disconnected
