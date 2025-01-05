import random
import unittest

from services.game import create_game, is_in_game, score, finish_match
from utils.my_unittest import UnitTest


class Test01_Game(UnitTest):

    def test_001_create_game(self):
        user1 = self.user(['game-start'])
        user2 = self.user(['game-start'])

        self.assertResponse(create_game(user1, user2), 201)
        self.assertThread(user1, user2)

    def test_002_already_in_game(self):
        user1 = self.user(['game-start'])
        user2 = self.user(['game-start'])

        self.assertResponse(is_in_game(user1), 404)
        self.assertResponse(create_game(user1, user2), 201)
        self.assertResponse(is_in_game(user1), 200)
        self.assertThread(user1, user2)

    def test_003_invalid_game_mode(self):
        user1 = self.user()
        user2 = self.user()

        self.assertResponse(create_game(user1, user2, game_mode='caca'), 400)
        self.assertThread(user1, user2)

    def test_004_no_game_mode(self):
        self.assertResponse(create_game(data={'teams': [[1], [2]]}), 400, {'game_mode': ['This field is required.']})

    def test_005_invalid_teams(self):
        invalid_teams = [
            [[], []],
            [[1], []],
            [[], [1]],
            [['coucou'], ['hey']],
            [[1, 2], [5]],
            [[1], [1]],
            [[1, 2, 3], [4, 5, 6]],
            ['bonjour'],
            [[1, 2, 3], 'bonjour'],
            [[1, 2, 3], 5],
        ]

        for invalid_team in invalid_teams:
            self.assertResponse(create_game(data={'game_mode': 'ranked', 'teams': invalid_team}), 400)

    def test_006_no_teams(self):
        self.assertResponse(create_game(data={'game_mode': 'ranked'}), 400, {'teams': ['This field is required.']})


class Test02_Score(UnitTest):

    def test_001_score(self):
        user1 = self.user(['game-start'])
        score_1 = random.randint(0, 2)
        user2 = self.user(['game-start'])
        score_2 = random.randint(0, 2)

        self.assertResponse(create_game(user1, user2), 201)
        for _ in range(score_1):
            self.assertResponse(score(user1['id']), 204)
        for _ in range(score_2):
            self.assertResponse(score(user2['id']), 204)
        response = self.assertResponse(is_in_game(user1), 200)
        self.assertEqual(score_1, response['teams']['a'][0]['score'])
        self.assertEqual(score_2, response['teams']['b'][0]['score'])
        self.assertThread(user1, user2)

    def test_002_not_in_game(self):
        user1 = self.user()

        self.assertResponse(score(user1['id']), 404, {'detail': 'This user does not belong to any match.'})
        self.assertThread(user1)


class Test03_Finish(UnitTest):

    def test_001_finish_game(self):
        user1 = self.user(['game-start'])
        user2 = self.user(['game-start'])

        self.assertResponse(create_game(user1, user2), 201)
        for _ in range(3):
            self.assertResponse(score(user1['id']), 204)
        self.assertThread(user1, user2)

    def test_002_finish_abandon(self):
        user1 = self.user(['game-start'])
        user2 = self.user(['game-start'])

        match_id = self.assertResponse(create_game(user1, user2), 201, get_field=True)
        for _ in range(2):
            self.assertResponse(score(user1['id']), 204)
        self.assertResponse(finish_match(match_id, 'player-disconnect', user2['id']), 200)
        self.assertThread(user1, user2)


if __name__ == '__main__':
    unittest.main()
