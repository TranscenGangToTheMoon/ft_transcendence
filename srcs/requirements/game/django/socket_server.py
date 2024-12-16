from aiohttp import web
from game_server.server import Server
import socketio

if __name__ == '__main__':
    Server.serve() # runs web.run_app(...)

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
