from aiohttp import web
from threading import Thread


async def create_game(request: web.Request):
    from game_server.server import Server
    # only accept requests from django (on the same host)
    if request.remote == '127.0.0.1':
        data = await request.post()
        match_id = data['match_id']
        Thread(target=Server.launch_game, args=(match_id,)).start()
    return web.Response()
