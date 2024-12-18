from logging import info, debug, error


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
        Server._clients[sid] = player
        print('Transport is : ', Server._sio.transport(sid), flush=True)
        await Server._sio.enter_room(sid, str(match_code))
    except Exception as e:
        error(e)
        raise ConnectionRefusedError('Player does not belong to any game')
    info('Client connected & authenticated')


async def move_up(sid):
    from game_server.server import Server
    player = Server._clients[sid]
    await Server._sio.emit(
        'move_up',
        data={'player': player.user_id},
        room=str(player.match_code),
        skip_sid=sid)
    player.racket.move_up()


async def move_down(sid):
    from game_server.server import Server
    player = Server._clients[sid]
    await Server._sio.emit(
        'move_down',
        data={'player': player.user_id},
        room=str(player.match_code),
        skip_sid=sid
    )
    player.racket.move_down()


async def stop_moving(sid, data):
    from game_server.server import Server
    player = Server._clients[sid]
    position = data['position']
    await Server._sio.emit(
        'stop_moving',
        data={'player': player.user_id, 'position': position},
        room=str(player.match_code),
        skip_sid=sid
    )
    player.racket.stop_moving()


async def send_games(sid):
    from game_server.server import Server
    codes = []
    for game in Server._games:
        codes.append(game)
    await Server._sio.emit('games', data=codes, to=sid)
    info(f'games are: {codes}')


async def goal(sid):
    from game_server.server import Server
    player = Server._clients[sid]
    Server._games[player.match_code].score()


async def bounce(sid, data):
    from game_server.server import Server
    player = Server._clients[sid]
    await Server._sio.emit('bounce', data={'dir_x': -data['dir_x'], 'dir_y': data['dir_y']}, skip_sid=sid)


async def disconnect(sid):
    from game_server.server import Server
    if Server._clients == {}:
        return
    match_code = Server._clients[sid].match_code
    await Server._sio.leave_room(sid, str(match_code))
