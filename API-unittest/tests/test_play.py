import time
import unittest

from services.game import create_game, is_in_game
from services.lobby import create_lobby, join_lobby
from services.play import play
from services.tournament import join_tournament, create_tournament
from utils.credentials import new_user, guest_user
from utils.my_unittest import UnitTest


class Test01_Play(UnitTest):

    def test_001_play_duel(self):
        self.assertResponse(play(), 201)

    def test_002_play_ranked(self):
        self.assertResponse(play(game_mode='ranked'), 201)

    def test_003_create_game(self):
        self.assertResponse(create_game(new_user(), new_user()), 201)


# todo remake if user find a match
class Test02_PlayError(UnitTest):

    def test_001_already_in_game(self):
        user1 = new_user()

        self.assertResponse(create_game(user1, new_user()), 201)
        self.assertResponse(play(user1), 409, {'detail': 'You are already in a game.'})

    def test_002_already_in_tournament(self):
        user1 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        for i in range(3):
            self.assertResponse(join_tournament(code), 201)

        self.assertResponse(play(user1), 409, {'detail': 'You are already in a tournament.'})

    def test_003_guest_cannot_play_ranked(self):
        self.assertResponse(play(guest_user(), 'ranked'), 403, {'detail': 'Guest users cannot play ranked games.'})

    def test_004_user_in_lobby(self):
        user1 = new_user()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(play(user1), 201)
        self.assertResponse(create_lobby(user1, method='GET'), 404, {'detail': 'You do not belong to any lobby.'})
        self.assertResponse(join_lobby(code, user1, 'GET'), 403, {'detail': 'You do not belong to this lobby.'})

    def test_005_user_in_tournament(self):
        user1 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(play(user1), 201)
        self.assertResponse(create_tournament(user1, method='GET'), 404, {'detail': 'You do not belong to any tournament.'})
        self.assertResponse(join_tournament(code, user1, 'GET'), 403, {'detail': 'You do not belong to this tournament.'})

    def test_006_delete(self):
        while True:
            user1 = new_user()

            self.assertResponse(play(user1), 201)
            time.sleep(1)
            response = is_in_game(user1)
            if response.status_code == 404:
                break

        self.assertResponse(play(user1, method='DELETE'), 204)

    def test_006_delete_not_play(self):
        self.assertResponse(play(method='DELETE'), 404, {'detail': 'You are not currently playing.'})


if __name__ == '__main__':
    unittest.main()
