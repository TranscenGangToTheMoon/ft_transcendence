import unittest

from services.stats import finish_match_stat, get_stats, get_ranked_stats
from utils.my_unittest import UnitTest


validata_data = {'id': 3, 'game_mode': 'duel', 'created_at': '2025-01-09T02:39:48.794986+01:00', 'game_duration': '00:00:05.206017', 'tournament_id': 1, 'tournament_stage_id': 2, 'tournament_n': 3, 'teams': {'a': [{'id': 6, 'username': 'user-UVGIYopESD', 'is_guest': False, 'profile_picture': None, 'status': {'is_online': True, 'game_playing': None, 'last_online': '2025-01-09T01:39:38.791177Z'}, 'trophies': 0, 'score': 0}], 'b': [{'id': 5, 'username': 'user-EXVoWJcIWJ', 'is_guest': False, 'profile_picture': None, 'status': {'is_online': True, 'game_playing': None, 'last_online': '2025-01-09T01:39:37.690417Z'}, 'trophies': 0, 'score': 3}]}, 'winner': 'b', 'looser': 'a', 'score_winner': 3, 'score_looser': 0}


class Test01_FinishMatch(UnitTest):

    def test_001_finish_match(self):
        self.assertResponse(finish_match_stat(validata_data), 201)

    def test_002_validation_error(self):
        self.assertResponse(finish_match_stat(), 400)
        self.assertResponse(finish_match_stat({**validata_data, 'game_mode': 'caca'}), 400)
        self.assertResponse(finish_match_stat({**validata_data, 'teams': 'caca'}), 400)
        self.assertResponse(finish_match_stat({**validata_data, 'teams': {'1': [], '2': []}}), 400)
        self.assertResponse(finish_match_stat({**validata_data, 'teams': {'a': [{'id': 6, 'score': 0}], 'b': [{'id': 5}]}}), 400)


class Test02_Stats(UnitTest):

    def test_001_stats(self):
        user1 = self.user()

        response = self.assertResponse(get_stats(user1), 200)
        self.assertEqual(response[0]['wins'], 0)
        data = validata_data
        data['teams']['b'][0]['id'] = user1['id']
        self.assertResponse(finish_match_stat(data), 201)
        response = self.assertResponse(get_stats(user1), 200)
        self.assertEqual(response[0]['wins'], 1)
        self.assertThread(user1)


class Test03_StatsRanked(UnitTest):

    def test_001_ranked_stats(self):
        user1 = self.user()

        self.assertResponse(get_ranked_stats(user1), 200)
        self.assertThread(user1)


if __name__ == '__main__':
    unittest.main()
