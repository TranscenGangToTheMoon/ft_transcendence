import unittest

from services.game import create_game, is_in_game
from utils.my_unittest import UnitTest


class Test01_Game(UnitTest):

    def test_001_create_game(self):
        self.assertResponse(create_game(self.new_user(get_me=True), self.new_user(get_me=True)), 201)

    def test_002_already_in_game(self):
        user1 = self.new_user(get_me=True)

        self.assertResponse(is_in_game(user1), 404)
        self.assertResponse(create_game(user1, self.new_user(get_me=True)), 201)
        self.assertResponse(is_in_game(user1), 200)

    def test_003_invalid_game_mode(self):
        self.assertResponse(create_game(self.new_user(get_me=True), self.new_user(get_me=True), game_mode='caca'), 400)

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


if __name__ == '__main__':
    unittest.main()
