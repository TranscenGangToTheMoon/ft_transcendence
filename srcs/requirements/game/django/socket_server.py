from aiohttp import web
from game_server.server import Server
from game_server import io_handlers
from game_server import requests_handlers
import socketio

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*', logger=True)
app = web.Application()
sio.attach(app, socketio_path='/ws/') #TODO -> change with '/ws/game/'
server = Server()
port = 5500


if __name__ == '__main__':
    app.add_routes([web.post('/create-game', requests_handlers.create_game)])

    sio.on('connect', handler=io_handlers.connect)
    sio.on('disconnect', handler=io_handlers.disconnect)
    sio.on('get_games', handler=io_handlers.send_games)
    sio.on('move_down', handler=io_handlers.move_down)
    sio.on('move_up', handler=io_handlers.move_up)
    sio.on('stop_moving', handler=io_handlers.stop_moving)

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
