from aiohttp import web
import sys

async def create_game(request: web.Request):
    from socket_server import server
    # only accept requests from django (on the same host)
    if request.remote == '127.0.0.1':
        data = await request.post()
        match_code = data['match_code']
        print('launching match ', match_code, flush=True)
        await server.launch_game(match_code)
    return web.Response()
