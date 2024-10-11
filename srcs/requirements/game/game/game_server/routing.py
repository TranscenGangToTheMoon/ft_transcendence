from django.urls import path
from views import game_server as gs_view

websocket_urlpatterns = [
	path('', gs_view),
	path('game_server/', gs_view),
]
