# from asgiref.sync import async_to_sync
from threading import Thread
from game_server.main import server

def launch_server(match):
    print('launching thread', flush=True)
    print(match.code)
    Thread(target=server.launch_game, args=(match.code,)).start()
