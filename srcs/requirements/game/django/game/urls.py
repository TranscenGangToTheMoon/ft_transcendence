from django.urls import path
from lib_transcendence.endpoints import Game

from matches.views import match_create_view, match_retrieve_view, match_list_view
from tournaments.views import save_tournament_view, retrieve_tournament_view

urlpatterns = [
    path(Game.match, match_create_view),
    path(Game.match_user, match_retrieve_view),
    path(Game.tournaments, save_tournament_view),

    path(Game.matches_user, match_list_view),
    path(Game.tournament, retrieve_tournament_view),
]
