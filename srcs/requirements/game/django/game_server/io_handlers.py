async def connect(sid, environ, auth):
    from socket_server import server, sio
    print('trying to connect', flush=True)
    if auth['token'] == 'kk':
        print(f"Client connecté : {sid}", flush=True)
    else:
        raise ConnectionRefusedError('Authentication failed')
    id = auth['id']
    print('id: ', id, flush=True)
    try:
        player, match_code = server.get_player_and_match_code(id)
        print('got player and its match_code', flush=True)
        player.socket_id = sid
        server.clients[sid] = player
    except Exception as e:
        print(e, flush=True)
        raise ConnectionRefusedError('Player does not belong to any game')
    print('registered a new racket', flush=True)


async def join_room(sid):
    from socket_server import server, sio
    id = server.clients[sid].user_id
    player, match_code = server.get_player_and_match_code(id)
    await sio.enter_room(sid, str(match_code))


async def move_up(sid):
    from socket_server import server, sio
    # player = server.clients[sid]
    # racket = server.
    # racket.move_up()
    await sio.emit('move_up')#, data={'player': player.user_id}, room=str(player.match_code), skip_sid=sid)


async def move_down(sid, data):
    from socket_server import server, sio
    player = server.clients[sid]
    racket = player.racket
    racket.move_down()
    await sio.emit('move_down', data={'player': player.user_id}, room=str(player.match_code), skip_sid=sid)


async def stop_moving(sid, data):
    from socket_server import server, sio
    player = server.clients[sid]
    racket = player.racket
    racket.stop_moving()
    await sio.emit('stop_moving', data={'player': player.user_id}, room=str(player.match_code), skip_sid=sid)


async def send_games(sid):
    from socket_server import server, sio
    codes = []
    for game in server.games:
        codes.append(game)
    await sio.emit('games', data=codes, to=sid)
    print(f'games are: {codes}', flush=True)


async def disconnect(sid):
    from socket_server import server, sio
    player = server.clients[sid]
    match_code = player.match_code
    await sio.leave_room(sid, str(match_code))
