from logging import info, debug, error


# TODO -> change this to use the Server class
async def connect(sid, environ, auth):
    from game_server.server import Server

    # Websockets Debug entrypoint
    if auth['token'] == 'debug': # TODO -> remove this in prod
        debug('Debug client connected')
        return True
    print('trying to connect', flush=True)
    # TODO -> do authentication here
    if auth['token'] != 'kk':
        error('Authentication failed')
        return False
    id = auth['id']
    print('id is : ', id, flush=True)
    try:
        player, match_id = Server.get_player_and_match_id(id)
        player.socket_id = sid
        Server._clients[sid] = player
        print('Transport is : ', Server._sio.transport(sid), flush=True)
        await Server._sio.enter_room(sid, str(match_id))
    except Exception as e:
        error(e)
        error('Player does not belong to any game')
        return False
    info('Client connected & authenticated')


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
