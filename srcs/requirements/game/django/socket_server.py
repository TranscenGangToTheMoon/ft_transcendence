from aiohttp import web
from game_server.server import Server
import socketio

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*', logger=True)
app = web.Application()
sio.attach(app, socketio_path='/ws/') #TODO -> change with '/ws/game/'
server = Server()
port = 5500


@sio.event
async def connect(sid, environ, auth):
    print('trying to connect', flush=True)
    if auth['token'] == 'kk':
        print(f"Client connecté : {sid}", flush=True)
    else:
        raise ConnectionRefusedError('Authentication failed')
    id = auth['id']
    try:
        player, match_code = server.get_player_and_match_code(id)
        player.socket_id = sid
        server.players[sid] = player
        await sio.enter_room(sid, str(match_code))
    except Exception as e:
        print(e, flush=True)
        raise ConnectionRefusedError('Player does not belong to any game')
    print('registered a new racket', flush=True)


@sio.event
async def move_up(sid, data):
    player = server.players[sid]
    racket = player.racket
    racket.move_up()
    await sio.emit('move_up', data={'player': player.user_id}, room=str(player.match_code), skip_sid=sid)

@sio.event
async def move_down(sid, data):
    player = server.players[sid]
    racket = player.racket
    racket.move_down()
    await sio.emit('move_down', data={'player': player.user_id}, room=str(player.match_code), skip_sid=sid)

@sio.event
async def stop_moving(sid, data):
    player = server.players[sid]
    racket = player.racket
    racket.stop_moving()
    await sio.emit('stop_moving', data={'player': player.user_id}, room=str(player.match_code), skip_sid=sid)


async def send_games(sid):
    codes = []
    for game in server.games:
        codes.append(game)
    await sio.emit('games', data=codes, to=sid)
    print(f'games are: {codes}', flush=True)
sio.on('get_games', handler=send_games)

@sio.event
async def disconnect(sid):
    player = server.players[sid]
    match_code = player.match_code
    await sio.leave_room(sid, str(match_code))


async def create_game(request: web.Request):
    if request.remote == '127.0.0.1':
        data = await request.post()
        match_code = data['match_code']
        print('launching match ', match_code, flush=True)
        await server.launch_game(match_code)
    return web.Response()

app.add_routes([web.post('/create-game', create_game)])


if __name__ == '__main__':
    server.serve(app, sio, port) # runs web.run_app(...)

'''
to send : position, direction et vitesse de la balle à 20fps
Position des joueurs
event -> move_up
event -> move_down
event -> stop_moving
event <- move_up {player_id: 1234}
event <- move_down {player_id: 1234}
event <- stop_moving {player_id: 1234}
event <- server_update
{
    ball: {
        x: 3,
        y: 4,
        direction: 91823750987
    },
    players: [
        {
            playerid: 1234,
            x: 3,
            y: 4
        },
        {
            playerid: 1234,
            x: 3,
            y: 4
        },
        {
            playerid: 1234,
            x: 3,
            y: 4
        }
    ]
}
'''
