from django.shortcuts import render


def game_server(request):
    return render(request, "game_server.html")
