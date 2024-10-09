from os import fork
from django.shortcuts import render
from gameserver import serve_game

def login(request):
	return render(request, 'game.html')
