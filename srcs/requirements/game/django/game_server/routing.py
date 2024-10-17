from django.urls import re_path
from . import client_handling

websocket_urlpatterns = [
	re_path('game_server/', client_handling.GameClient.as_asgi()),
]
