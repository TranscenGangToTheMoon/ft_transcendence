import unittest

from services.game import create_game, is_in_game
from utils.credentials import new_user
from utils.my_unittest import UnitTest

# todo test
# todo test already in game
# todo test game
# todo test not same nb of user in team
# todo test not team
# todo test invalide team
# todo test invlaid game mode


class Test01_Game(UnitTest):

    def test_001_create_game(self):
        self.assertResponse(create_game(new_user(), new_user()), 201)


    def test_003_invalid_game_mode(self):
        self.assertResponse(create_game(new_user(), new_user(), game_mode='caca'), 400)


if __name__ == '__main__':
    unittest.main()
