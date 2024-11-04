from django.db import models
from play.models import Players

def makeMatch(request):
	players = Players.objects.filter(game_mode='duel').order_by('join_at')
	while (players.exists and players.count() >= 2):
		player1 = players[0];
		player2 = players[1];


	return players
