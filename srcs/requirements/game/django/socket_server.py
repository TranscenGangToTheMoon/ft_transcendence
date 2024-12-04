from aiohttp import web
from game_server.server import Server
import socketio

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)
server = Server()
port = 5500


@sio.event
async def connect(sid, environ):
    print(f"Client connecté : {sid}", flush=True)


@sio.event
async def chat_message(sid, data):
    print("message ", data)

async def send_games(sid):
    # games = {server.games.match_code: match.code}
    codes = []
    for game in Server.games:
        codes.append(game)
    await sio.emit('games', data=codes, to=sid)
    print('sending games', flush=True)
    print(f'games are: {codes}', flush=True)
sio.on('get_games', handler=send_games)

@sio.event
def disconnect(sid):
    print('disconnected', sid, flush=True)


# def run_server():
#     global app, sio, port
#     server.serve(app, sio, port) # runs web.run_app(...)


async def create_game(request: web.Request):
    print('received create_game request', flush=True)
    print(f'host is {request.remote}', flush=True)
    if request.remote == '127.0.0.1':
        print('request has been accepted', flush=True)
        data = await request.post()
        match_code = data['match_code']
        print('match_code : ', match_code, flush=True)
        await server.launch_game(match_code)
    return web.Response()

app.add_routes([web.post('/create-game', create_game)])


if __name__ == '__main__':
    server.serve(app, sio, port) # runs web.run_app(...)
