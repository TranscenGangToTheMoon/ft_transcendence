from django.urls import path
from lib_transcendence.endpoints import Matchmaking, UsersManagement

from lobby.views import lobby_view, lobby_participants_view, lobby_kick_view
from play.views import duel_view, ranked_view
from tournament.views import tournament_view, tournament_search_view, tournament_participants_view, tournament_kick_view, \
    tournament_result_match_view
from user_management.views import blocked_user_view, delete_user_view

urlpatterns = [
    path(Matchmaking.duel, duel_view),
    path(Matchmaking.ranked, ranked_view),

    path(Matchmaking.lobby, lobby_view),
    path(Matchmaking.lobby_participant, lobby_participants_view),
    path(Matchmaking.lobby_kick, lobby_kick_view),

    path(Matchmaking.tournament, tournament_view),
    path(Matchmaking.tournament_search, tournament_search_view),
    path(Matchmaking.tournament_participant, tournament_participants_view),
    path(Matchmaking.tournament_kick, tournament_kick_view),

    path(Matchmaking.tournament_result_match, tournament_result_match_view),

    path(UsersManagement.blocked_user, blocked_user_view),
    path(UsersManagement.delete_user, delete_user_view),
]
