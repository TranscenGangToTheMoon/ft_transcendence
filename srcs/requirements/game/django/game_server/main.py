from aiohttp import web
from game_server.socket_init import init_socketIO
from game_server.server import Server
import socketio

# SocketIO setup
sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)
server = Server()

async def game_server():
    global sio, app, server
    init_socketIO(server, sio)
    await server.serve(app, sio)
