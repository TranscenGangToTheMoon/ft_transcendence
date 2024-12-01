from django.urls import path
from lib_transcendence.endpoints import Game

from matches.views import create_match_view, list_matches_view, retrieve_match_view
from tournaments.views import save_tournament_view, retrieve_tournament_view

urlpatterns = [
    path(Game.match, create_match_view),
    path(Game.match_user, retrieve_match_view),
    path(Game.matches_user, list_matches_view),

    path(Game.tournaments, save_tournament_view),
    path(Game.tournament, retrieve_tournament_view),
]
