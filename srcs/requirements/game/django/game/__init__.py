from threading import Thread
import time

def wait_then_launch():
	time.sleep(10)
	from .game_launcher import create_game
	create_game()

thread = Thread(target=wait_then_launch).start()
print("Started game server")
