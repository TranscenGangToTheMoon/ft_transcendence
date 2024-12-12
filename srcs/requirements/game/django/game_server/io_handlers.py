from logging import info, debug, warning, error


async def connect(sid, environ, auth):
    from game_server.server import Server

    # Websockets Debug entrypoint
    if auth['token'] == 'debug': # TODO -> remove this in prod
        debug('Debug client connected')
        return True

    # TODO -> do authentication here
    if auth['token'] != 'kk':
        raise ConnectionRefusedError('Authentication failed')
    id = auth['id']
    try:
        player, match_code = Server.get_player_and_match_code(id)
        player.socket_id = sid
        Server.clients[sid] = player
        info('Transport is : ', Server.sio.transport(sid))
        await Server.sio.enter_room(sid, str(match_code))
    except Exception as e:
        error(e)
        raise ConnectionRefusedError('Player does not belong to any game')
    info('Client connected & authenticated')


async def move_up(sid):
    from game_server.server import Server
    player = Server.clients[sid]
    await Server.sio.emit(
        'move_up',
        data={'player': player.user_id},
        room=str(player.match_code),
        skip_sid=sid)
    player.racket.move_up()


async def move_down(sid):
    from game_server.server import Server
    player = Server.clients[sid]
    await Server.sio.emit(
        'move_down',
        data={'player': player.user_id},
        room=str(player.match_code),
        skip_sid=sid
    )
    player.racket.move_down()


async def stop_moving(sid):
    from game_server.server import Server
    player = Server.clients[sid]
    await Server.sio.emit(
        'stop_moving',
        data={'player': player.user_id},
        room=str(player.match_code),
        skip_sid=sid
    )
    player.racket.stop_moving()


async def send_games(sid):
    from game_server.server import Server
    codes = []
    for game in Server.games:
        codes.append(game)
    await Server.sio.emit('games', data=codes, to=sid)
    info(f'games are: {codes}')


async def disconnect(sid):
    from game_server.server import Server
    match_code = Server.clients[sid].match_code
    await Server.sio.leave_room(sid, str(match_code))
