from django.urls import path

from lib_transcendence.endpoints import Game, UsersManagement
from matches.views import create_match_view, create_match_not_played_view, list_matches_view, retrieve_user_match_view, retrieve_match_view, finish_match_view, score_view
from tournaments.views import save_tournament_view, retrieve_tournament_view
from user_management.views import export_data_view

urlpatterns = [
    path(Game.create_match, create_match_view),
    path(Game.create_match_not_played, create_match_not_played_view),
    path(Game.finish_match, finish_match_view),
    path(Game.score, score_view),
    path(Game.user, retrieve_user_match_view),
    path(Game.match_user, retrieve_match_view),
    path(Game.matches_user, list_matches_view),

    path(UsersManagement.export_data, export_data_view),

    path(Game.tournaments, save_tournament_view),
    path(Game.tournament, retrieve_tournament_view),
]
