import time
from aiohttp import web
from server import Server
import asyncio
import socketio
from socket_init import init_socketIO
import sys
from get_match import get_match

# SocketIO setup
sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)
init_socketIO(sio)

async def main():
    try:
        match_id = int(sys.argv[1])
        server = Server()
        await server.serve(app, sio)
    except Exception:
        return 1
    await get_match(match_id)
    server.init_game()
    while True:
        time.sleep(1)
    # server.launch_game()
    # TODO -> make server.launch_game()

if __name__ == '__main__':
    asyncio.run(main())
