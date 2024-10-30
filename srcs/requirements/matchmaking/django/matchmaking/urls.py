from django.urls import path

from lobby.views import lobby_view, lobby_participants_view, lobby_kick_view
from play.views import duel_view, ranked_view
from tournament.views import tournament_view, tournament_search_view, tournament_participants_view, tournament_kick_view, \
    tournament_result_match_view

urlpatterns = [
    path('api/play/duel/', duel_view),
    path('api/play/ranked/', ranked_view),

    path('api/play/lobby/', lobby_view),
    path('api/play/lobby/<str:code>/', lobby_participants_view),
    path('api/play/lobby/<str:code>/kick/<int:user_id>/', lobby_kick_view),

    path('api/play/tournament/', tournament_view),
    path('api/play/tournament/search/', tournament_search_view),
    path('api/play/tournament/<str:code>/', tournament_participants_view),
    path('api/play/tournament/<str:code>/kick/<int:user_id>/', tournament_kick_view),

    path('api/tournament/result-match/', tournament_result_match_view),
]
