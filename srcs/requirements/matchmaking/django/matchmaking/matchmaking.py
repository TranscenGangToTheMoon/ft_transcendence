from .create_match import create_match
from datetime import datetime, timezone
from lib_transcendence.game import GameMode
from rest_framework.exceptions import APIException


def launch_dual_game(players):
	player1 = players[0]
	player2 = players[1]

	create_match(GameMode.duel, [[player1.user_id], [player2.user_id]])
	#print('made request for: ', player1.user_id, ' ', player1.trophies, ' ', player2.user_id, ' ', player2.trophies, flush=True)
	player1.delete()
	player2.delete()


	#print('Normal Game created=============')


def get_optimal_rank_range(player):
	waiting_time = datetime.now(timezone.utc) - player.join_at
	optimal_range = waiting_time.total_seconds() / 15
	if optimal_range > 5:
		return 5
	return optimal_range


def order_by_rank_difference(players_query_set, base_rank):
	return sorted(players_query_set, key=lambda x: abs(x.trophies - base_rank))


def search_ranked_players(ranked_players):
	for player in ranked_players:
		optimal_range = get_optimal_rank_range(player) * 1000

		potential_mates = order_by_rank_difference(
			ranked_players
			.exclude(user_id=player.user_id)
			.filter(trophies__range=(player.trophies, int(optimal_range))), player.trophies)

		mate = potential_mates[0] if potential_mates else None
		if mate is not None:
			try:
				# post_match(player, mate, GameMode.ranked)
				return True
			except APIException:
				pass
	return False

# def launch_matchmaking(request):
# 	while (True):
# 		sleep(1)
# 		make_match()
# 	return response.HttpResponse('<h1>Matchmaking started<h1/>', status=status.HTTP_200_OK)
