from aiohttp import web
from game_server.server import Server
import socketio

if __name__ == '__main__':
    Server.serve()
