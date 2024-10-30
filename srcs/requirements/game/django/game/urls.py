from django.urls import path

from game_server.views import game_server
from matches.views import match_create_view, match_list_view, playing_view
from tournaments.views import save_tournament_view, retrieve_tournament_view

urlpatterns = [
    path('game/', game_server),

    path('api/match/', match_create_view),
    path('api/playing/<int:user_id>/', playing_view),
    path('api/tournaments/', save_tournament_view),

    path('api/game/match/<int:user_id>/', match_list_view),
    path('api/game/tournaments/<int:pk>/', retrieve_tournament_view),
]
