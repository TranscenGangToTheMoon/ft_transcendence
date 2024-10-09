from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

game_list = []

def serve_game(game_id):
	game_list.append(game_id);
	return True
