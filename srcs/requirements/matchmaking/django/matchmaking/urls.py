from django.urls import path

from baning.views import lobby_ban_view, tournament_ban_view
from blocking.views import blocked_user_view
from invite.views import lobby_invite_view, tournament_invite_view
from lib_transcendence.endpoints import Matchmaking, UsersManagement
from lobby.views import lobby_view, lobby_participants_view, lobby_finish_match_view
from message.views import lobby_message_view, tournament_message_view
from play.views import duel_view, ranked_view
from tournament.views import tournament_view, tournament_search_view, tournament_participants_view, \
    tournament_result_match_view
from user_management.views import delete_user_view

urlpatterns = [
    path(Matchmaking.duel, duel_view),
    path(Matchmaking.ranked, ranked_view),

    path(Matchmaking.lobby, lobby_view),
    path(Matchmaking.lobby_participant, lobby_participants_view),
    path(Matchmaking.lobby_finish_match, lobby_finish_match_view),
    path(Matchmaking.lobby_invite, lobby_invite_view),
    path(Matchmaking.lobby_ban, lobby_ban_view),
    path(Matchmaking.lobby_message, lobby_message_view),

    path(Matchmaking.tournament, tournament_view),
    path(Matchmaking.tournament_search, tournament_search_view),
    path(Matchmaking.tournament_participant, tournament_participants_view),
    path(Matchmaking.tournament_invite, tournament_invite_view),
    path(Matchmaking.tournament_ban, tournament_ban_view),
    path(Matchmaking.tournament_message, tournament_message_view),

    path(Matchmaking.tournament_result_match, tournament_result_match_view),

    path(UsersManagement.blocked_user, blocked_user_view),
    path(UsersManagement.delete_user, delete_user_view),
]
