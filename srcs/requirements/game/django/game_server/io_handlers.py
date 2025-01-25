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


async def connect(sid, environ, auth):
    from game_server.server import Server
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
    print(f'User {id} connecting...{sid}', flush=True)
    try:
        match = request_game(endpoints.Game.fuser.format(user_id=id), 'GET')
    except NotFound as e:
        match_code = auth.get('match_code')
        if match_code is None:
            raise ConnectionRefusedError(e.detail)
        try:
            game = Server.get_game(match_code)
        except Server.NotFound:
            return False
        if game.match.game_type == 'normal':
            game.add_spectator(id, sid)
            await Server._sio.enter_room(sid, str(game.match.id))
            return True
        else:
            return False
    except APIException as e:
        raise ConnectionRefusedError(MessagesException.ServiceUnavailable.game)
    if match is None:
        raise ConnectionRefusedError(MessagesException.ServiceUnavailable.game)
    try:
        game_data = request_game(endpoints.Game.fmatch_user.format(user_id=id, match_id=match['id']), 'GET')
    except NotFound as e:
        raise ConnectionRefusedError(e.detail)
    except APIException as e:
        raise ConnectionRefusedError(MessagesException.ServiceUnavailable.game)
    if game_data is None:
        raise ConnectionRefusedError(MessagesException.ServiceUnavailable.game)
    game_id = game_data['id']
    if not Server.does_game_exist(game_id):
        match = Match(game_data)
        Server.create_game(match)
    player = Server.get_player(id)
    player_sid = player.socket_id
    print(f'player sid: {player_sid}', flush=True)
    if player_sid != '' and player_sid != sid:
        await Server._sio.leave_room(player_sid, str(player.match_id))
        with Server._dsids_lock:
            Server._disconnected_sids.append(player_sid)
        await Server._sio.disconnect(player_sid)
    player.socket_id = sid
    Server._clients[sid] = player
    await Server._sio.enter_room(sid, str(game_id))
    print(f'User {id} connected & authenticated', flush=True)


async def move_up(sid):
    from game_server.server import Server
    try:
        player = Server._clients[sid]
        await Server._sio.emit(
            'move_up',
            data={'player': player.user_id},
            room=str(player.match_id),
            skip_sid=sid)
        player.racket.move_up()
    except KeyError:
        pass


async def move_down(sid):
    from game_server.server import Server
    try:
        player = Server._clients[sid]
        await Server._sio.emit(
            'move_down',
            data={'player': player.user_id},
            room=str(player.match_id),
            skip_sid=sid
        )
        player.racket.move_down()
    except KeyError:
        pass


async def stop_moving(sid, data):
    from game_server.server import Server
    try:
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
    except KeyError:
        pass


async def disconnect(sid):
    from game_server.server import Server
    with Server._dsids_lock:
        for search in Server._disconnected_sids:
            if search == sid:
                Server._disconnected_sids.remove(sid)
                return
                ''' the client did try to connect with two
                different sids simultaneously,
                causing the first to be disconnected,
                no need to finish the game
                '''
    try:
        client = Server._clients[sid]
        client.socket_id = ''
        client.racket.stop_moving(client.racket.position.y)
        Server._clients.pop(sid)
    except KeyError:
        pass # the client was a spectator or has already been disconnected, nothing alarming
