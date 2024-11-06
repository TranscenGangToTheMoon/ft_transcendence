import sys
import os

from django.http import response
from rest_framework import status
# sys.path.append(os.path.abspath('./'))
# print(os.listdir('./'))
# print(sys.path.__str__())
import datetime
from lib_transcendence.GameMode import GameMode
from lib_transcendence.request import ParseError
from lib_transcendence.services import requests_game
from rest_framework.exceptions import APIException
from datetime import datetime, timezone, timedelta
from play.models import Players
import time
from threading import Thread
from math import sqrt

def post_match(player1, player2, game_mode):
	requests_game('match/', 'POST', {'game_mode': game_mode, 'teams': [[player1.user_id], [player2.user_id]]}) #todo check for status code
	print('made request for: ', player1.user_id, ' ', player1.trophies, ' ', player2.user_id, ' ', player2.trophies, flush=True)
	player1.delete()
	player2.delete()

def get_optimal_rank_range(player):
	waiting_time = datetime.now(timezone.utc) - player.join_at
	optimal_range = waiting_time.total_seconds() / 15
	if optimal_range > 5:
		return 5
	return optimal_range

def order_by_rank_difference(players_query_set, base_rank):
	return sorted(players_query_set, key=lambda x: abs(x.trophies - base_rank))

def find_ranked_match(ranked_players):
	for player in ranked_players:
		optimal_range = get_optimal_rank_range(player) * 1000

		potential_mates = order_by_rank_difference(
			ranked_players
			.exclude(user_id=player.user_id)
			.filter(trophies__range=(player.trophies, int(optimal_range))),
		player.trophies)

		mate = potential_mates[0] if potential_mates else None
		if (mate is not None):
			try:
				post_match(player, mate, GameMode.ranked)
				return True
			except(APIException):
				pass
	return False

def make_match():
	players = Players.objects.all().order_by('join_at')
	count = players.count()
	while (players.count() >= 2):
		duel_players = players.filter(game_mode=GameMode.duel)
		if (duel_players.exists() and duel_players.count() >= 2):
			try:
				post_match(duel_players[0], duel_players[1], GameMode.duel)
			except(APIException):
				pass
				# todo inform client
		ranked_players = players.filter(game_mode=GameMode.ranked)
		find_ranked_match(ranked_players)
					# todo -> inform client
					# todo -> blocked user can't play together
	return "finished matchmaking"

def launch_matchmaking(request):
	# while (True):
	# 	time.sleep(5)
	# 	make_match()
	thread = Thread(target=make_match).start()
	return response.HttpResponse('<h1>Matchmaking started<h1/>', status=status.HTTP_200_OK)
