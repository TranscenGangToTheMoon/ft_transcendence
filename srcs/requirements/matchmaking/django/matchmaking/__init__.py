from .lookup import RangeLookup
from threading import Thread
import time

def wait_then_launch():
	time.sleep(10)
	from .matchmaking import make_match
	make_match()

thread = Thread(target=wait_then_launch).start()
