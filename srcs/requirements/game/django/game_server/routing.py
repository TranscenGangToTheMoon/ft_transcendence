from django.urls import re_path
from . import gameClient

websocket_urlpatterns = [
	re_path('game_server/', gameClient.GameClient.as_asgi()),
]
