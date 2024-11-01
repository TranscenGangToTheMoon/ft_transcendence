"""
URL configuration for matchmaking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from lobby.views import lobby_create_update_view, lobby_create_list_delete_view
from tournament.views import tournament_view, tournament_participants_view, tournament_kick_view, \
    tournament_result_match_view

urlpatterns = [
    path('api/play/lobby/', lobby_create_update_view),
    path('api/play/lobby/<str:code>/', lobby_create_list_delete_view),
    path('api/play/tournament/', tournament_view),
    path('api/play/tournament/<str:code>/', tournament_participants_view),
    path('api/play/tournament/<str:code>/kick/<int:user_id>/', tournament_kick_view),
    path('api/tournament/result-match/', tournament_result_match_view),
]
