from lib_transcendence.auth import auth_verify
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
    token = auth.get('token')
    if token is None:
        raise ConnectionRefusedError(MessagesException.Authentication.NOT_AUTHENTICATED)
    token = 'Bearer ' + token
    try:
        user_data = auth_verify(token)
    except APIException as e:
        raise ConnectionRefusedError(e.detail)
    id = user_data['id']
    try:
        game_data = request_game(endpoints.Game.fmatch_user.format(user_id=id), 'GET')
    except NotFound as e:
        raise ConnectionRefusedError(e.detail)
    except APIException as e:
        raise ConnectionRefusedError(MessagesException.ServiceUnavailable.game)
    game_id = game_data['id']
    if not Server.does_game_exist(game_id):
        match = Match(game_data)
        Thread(target=Server.launch_game, args=(match, )).start()
    player = Server.get_player(id)
    player.socket_id = sid
    Server._clients[sid] = player
    await Server._sio.enter_room(sid, str(game_id))
    info(f'User {id} connected & authenticated')


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
    position = data['position']
    position = player.racket.stop_moving(position)
    await Server._sio.emit(
        'stop_moving',
        data={'player': player.user_id, 'position': position},
        room=str(player.match_id)
    )


async def disconnect(sid):
    from game_server.server import Server
    if Server._clients == {}:
        return
    match_id = Server._clients[sid].match_id
    try:
        game = Server._games[match_id]
        game.finish('A player has disconnected')
        # TODO -> change this to avoid django exception on async context (sync_to_async)
    except KeyError:
        pass # if the game is not registered, it means the game has already finished
    await Server._sio.leave_room(sid, str(match_id))
