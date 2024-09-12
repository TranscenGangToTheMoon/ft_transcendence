from inspect import getfile
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

def index(request):
	# http = getfile("../../../game/frontend/game.html")
	http = "bite"
	return HttpResponse(http)
