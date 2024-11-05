from lib_transcendence.GameMode import GameMode
from lib_transcendence.request import ParseError
from lib_transcendence.services import requests_game
from requests.api import delete
from rest_framework.exceptions import APIException
from play.models import Players


def post_match(player1, player2, game_mode):
	requests_game('match/', 'POST', {'game_mode': game_mode, 'teams': [[player1.user_id], [player2.user_id]]}) #todo check for status code
	player1.delete()
	player2.delete()

def get_optimal_rank_range(player1, player2):
	max_time = max(player1.join_at, player2.join_at)
	return max_time.seconds / 15

def order_by_rank_difference(players_query_set, base_rank):
	sorted(players_query_set, key=lambda x: abs(x.trophies - base_rank))

def make_match():
	while (True):
		players = Players.objects.all().order_by('join_at')
		duel_players = players.filter(game_mode=GameMode.duel)
		if (duel_players.exists and duel_players.count() >= 2):
			try:
				post_match(duel_players[0].user_id, duel_players[1].user_id, GameMode.duel)
			except(APIException):
				pass
				# todo inform client
		ranked_players = players.filter(game_mode=GameMode.ranked)
		ranked_player1 = ranked_players.first()
		if (ranked_player1 is not None):
			ranked_player2 = ranked_players.exclude(user_id=ranked_player1.user_id).filter(rank__rng=[]).order_by('trophies').first()
			if (ranked_player2 is not None):
				try:
					post_match(ranked_player1.user_id, ranked_player2.user_id, GameMode.ranked)
				except(APIException):
					pass
					# todo inform client
