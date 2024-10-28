"""
URL configuration for game project.

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
