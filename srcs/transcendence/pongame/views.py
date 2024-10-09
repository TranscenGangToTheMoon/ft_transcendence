from os import fork
from django.shortcuts import render
from pongame.gameserver import serve_game

def game(request):
	return render(request, 'game.html')
