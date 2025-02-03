import asyncio
from socketio.exceptions import ConnectionRefusedError as socketioConnectError
from lib_transcendence.auth import auth_verify
from lib_transcendence.exceptions import MessagesException
from rest_framework.exceptions import NotFound
from lib_transcendence.services import request_game
from lib_transcendence import endpoints
from rest_framework.exceptions import APIException
from game_server.match import Match


async def disconnect_old_session(old_sid, player, game_id, new_sid):
    from game_server.server import Server
    await Server._sio.leave_room(old_sid, str(player.match_id))
    game = Server.get_game(game_id)
    if game.match.game_type == 'clash':
        raise socketioConnectError()
    await asyncio.sleep(1)
    try:
        await Server._sio.get_session(old_sid)
        await Server._sio.disconnect(old_sid)
        with Server._dsids_lock:
            Server._disconnected_sids.append(old_sid)
        await asyncio.sleep(0.5)
    except KeyError:
        pass
    game.reconnect(player.user_id, new_sid)


async def handle_spectator(user_id, sid, auth, match_code):
    from game_server.server import Server
    try:
        game = Server.get_game_from_code(match_code)
    except Server.NotFound as e:
        raise socketioConnectError(e)
    if game.match.game_type == 'normal':
        game.add_spectator(user_id, sid)
        await Server._sio.enter_room(sid, str(game.match.id))
        return True
    else:
        return False


async def accept_connection(player, sid, game_id):
    from game_server.server import Server
    player.socket_id = sid
    player.game = Server.get_game(game_id)
    Server._clients[sid] = player
    await Server._sio.enter_room(sid, str(game_id))


def fetch_data(endpoint) -> dict:
    try:
        data = request_game(endpoint, 'GET')
    except NotFound as e:
        raise socketioConnectError(e.detail)
    except APIException:
        raise socketioConnectError(MessagesException.ServiceUnavailable.game)
    if data is None:
        raise socketioConnectError(MessagesException.ServiceUnavailable.game)
    return data


async def connect(sid, environ, auth):
    from game_server.server import Server
    token = auth.get('token')
    if token is None:
        raise socketioConnectError(MessagesException.Authentication.NOT_AUTHENTICATED)
    token = 'Bearer ' + token
    try:
        user_data = auth_verify(token)
    except APIException as e:
        raise socketioConnectError(e.detail)
    if user_data is None:
        raise socketioConnectError(MessagesException.Authentication.NOT_AUTHENTICATED)
    id = user_data['id']
    match_code = auth.get('match_code')
    if match_code is not None:
        return await handle_spectator(id, sid, auth, match_code)
    match = fetch_data(endpoints.Game.fuser.format(user_id=id))
    game_data = fetch_data(endpoints.Game.fmatch_user.format(user_id=id, match_id=match['id']))
    game_id = game_data['id']
    if not Server.does_game_exist(game_id):
        match = Match(game_data)
        Server.create_game(match)
    player = Server.get_player(id)
    player_sid = player.socket_id
    if player_sid != '' and player_sid != sid:
        player.socket_id = ''
        await disconnect_old_session(player_sid, player, game_id, sid)
    await accept_connection(player, sid, game_id)


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
    try:
        match_id = Server._clients[sid].game.match.id
        await Server._sio.leave_room(sid, str(match_id))
    except KeyError:
        pass
    with Server._dsids_lock:
        for search in Server._disconnected_sids:
            try:
                await Server._sio.get_session(search)
            except KeyError:
                Server._disconnected_sids.remove(search)
                continue
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
        client.racket.stop_moving(client.racket.position.y)
        Server._clients[sid].socket_id = ''
        Server._clients.pop(sid)
        Server.emit(
            'stop_moving',
            {
                'player': client.user_id,
                'position': client.racket.position.y
            },
            str(client.match_id)
        )
    except KeyError:
        match_id = Server.get_spectator_match_id(sid)
        if match_id is not None:
            await Server.remove_spectator(sid, match_id)
