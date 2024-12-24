import time
import unittest

from services.game import create_game, is_in_game
from services.lobby import create_lobby, join_lobby
from services.play import play
from services.tournament import join_tournament, create_tournament
from utils.my_unittest import UnitTest


# todo  si pas connecter tu peux pas jouer matchmaking


class Test01_Play(UnitTest):

    def test_001_play_duel(self):
        user1 = self.user_sse()

        self.assertResponse(play(user1), 201)

    def test_002_play_ranked(self):
        user1 = self.user_sse()

        self.assertResponse(play(user1, game_mode='ranked'), 201)


class Test02_PlayError(UnitTest):

    def test_001_already_in_game(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        self.assertResponse(create_game(user1, user2), 201)
        self.assertResponse(play(user1), 409, {'detail': 'You are already in a game.'})

    def test_002_already_in_tournament(self):
        user1 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        for i in range(3):
            user_tmp = self.user_sse()
            self.assertResponse(join_tournament(user_tmp, code), 201)

        self.assertResponse(play(user1), 409, {'detail': 'You are already in a tournament.'})

    def test_003_guest_cannot_play_ranked(self):
        self.assertResponse(play(self.guest_user(), 'ranked'), 403, {'detail': 'Guest users cannot play ranked games.'})

    def test_004_user_in_lobby(self):
        user1 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(play(user1), 201)
        self.assertResponse(create_lobby(user1, method='GET'), 404, {'detail': 'You do not belong to any lobby.'})
        self.assertResponse(join_lobby(user1, code, 'GET'), 403, {'detail': 'You do not belong to this lobby.'})

    def test_005_user_in_tournament(self):
        user1 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(play(user1), 201)
        self.assertResponse(create_tournament(user1, method='GET'), 404, {'detail': 'You do not belong to any tournament.'})
        self.assertResponse(join_tournament(user1, code, 'GET'), 403, {'detail': 'You do not belong to this tournament.'})

    def test_006_delete(self):
        while True:
            user1 = self.user_sse()

            self.assertResponse(play(user1), 201)
            time.sleep(1)
            response = is_in_game(user1)
            if response.status_code == 404:
                break

        self.assertResponse(play(user1, method='DELETE'), 204)

    def test_006_delete_not_play(self):
        user1 = self.user_sse()

        self.assertResponse(play(user1, method='DELETE'), 404, {'detail': 'You are not currently playing.'})


if __name__ == '__main__':
    unittest.main()
