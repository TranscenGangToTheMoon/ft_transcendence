
async def connect(sid, environ, auth):
    from game_server.server import Server
    print(Server.sio, flush=True)
    print('trying to connect', flush=True)
    if auth['token'] == 'kk':
        print(f"Client connecté : {sid}", flush=True)
    else:
        raise ConnectionRefusedError('Authentication failed')
    id = auth['id']
    print('id: ', id, flush=True)
    try:
        player, match_code = Server.get_player_and_match_code(id)
        print('got player and its match_code', flush=True)
        player.socket_id = sid
        Server.clients[sid] = player
        await Server.sio.enter_room(sid, str(match_code))
    except Exception as e:
        print(e, flush=True)
        raise ConnectionRefusedError('Player does not belong to any game')
    print('registered a new racket', flush=True)


async def move_up(sid):
    from game_server.server import Server
    player = Server.clients[sid]
    player.racket.move_up()
    await Server.sio.emit(
        'move_up',
        data={'player': player.user_id},
        room=str(player.match_code),
        skip_sid=sid)


async def move_down(sid, data):
    from game_server.server import Server
    player = Server.clients[sid]
    player.racket.move_down()
    await Server.sio.emit('move_down', data={'player': player.user_id}, room=str(player.match_code), skip_sid=sid)


async def stop_moving(sid, data):
    from game_server.server import Server
    player = Server.clients[sid]
    player.racket.stop_moving()
    await Server.sio.emit('stop_moving', data={'player': player.user_id}, room=str(player.match_code), skip_sid=sid)


async def send_games(sid):
    from game_server.server import Server
    codes = []
    for game in Server.games:
        codes.append(game)
    await Server.sio.emit('games', data=codes, to=sid)
    print(f'games are: {codes}', flush=True)


async def disconnect(sid):
    from game_server.server import Server
    match_code = Server.clients[sid].match_code
    await Server.sio.leave_room(sid, str(match_code))
