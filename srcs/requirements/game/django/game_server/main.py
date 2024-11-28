from aiohttp import web
from server import Server
import asyncio
import socketio
from socket_init import init_socketIO
from match import request_match, Match
import sys

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
    match: Match = await request_match(match_id)
    await server.init_game(match)
    while True:
        await asyncio.sleep(1)
    # server.launch_game()
    # TODO -> make server.launch_game()

if __name__ == '__main__':
    asyncio.run(main())
