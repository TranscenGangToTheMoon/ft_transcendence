import time
import unittest

from services.game import create_game, is_in_game
from services.lobby import create_lobby, join_lobby
from services.play import play
from services.tournament import join_tournament, create_tournament
from utils.my_unittest import UnitTest


class Test01_Play(UnitTest):

    def test_001_play_duel(self):
        user1 = self.user(['game-start'])
        user2 = self.user(['game-start'])

        self.assertResponse(play(user1), 201)
        self.assertResponse(play(user2), 201)
        self.assertThread(user1, user2)

    def test_002_play_ranked(self):
        user1 = self.user()

        self.assertResponse(play(user1, game_mode='ranked'), 201)
        self.assertThread(user1)


class Test02_PlayError(UnitTest):

    def test_001_already_in_game(self):
        user1 = self.user(['game-start'])
        user2 = self.user(['game-start'])

        self.assertResponse(create_game(user1, user2), 201)
        self.assertResponse(play(user1), 409, {'detail': 'You are already in a game.'})
        self.assertThread(user1, user2)

    def test_002_already_in_tournament(self):
        user1 = self.user(['tournament-join', 'tournament-join', 'tournament-join', 'game-start'])
        users = [self.user(['tournament-join'] * (2 - i)) for i in range(3)]

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        for user_tmp in users:
            self.assertResponse(join_tournament(user_tmp, code), 201)

        self.assertResponse(play(user1), 409, {'detail': 'You are already in a tournament.'})
        self.assertThread(user1, *users)

    def test_003_guest_cannot_play_ranked(self):
        user1 = self.user(guest=True)

        self.assertResponse(play(user1, 'ranked'), 403, {'detail': 'Guest users cannot perform this action.'})
        self.assertThread(user1)

    def test_004_user_in_lobby(self):
        user1 = self.user(['game-start'])

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(play(user1), 201)
        self.assertResponse(create_lobby(user1, method='GET'), 404, {'detail': 'You do not belong to any lobby.'})
        self.assertResponse(join_lobby(user1, code, 'GET'), 403, {'detail': 'You do not belong to this lobby.'})
        self.assertThread(user1)

    def test_005_user_in_tournament(self):
        user1 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(play(user1), 201)
        self.assertResponse(create_tournament(user1, method='GET'), 404, {'detail': 'You do not belong to any tournament.'})
        self.assertResponse(join_tournament(user1, code, 'GET'), 403, {'detail': 'You do not belong to this tournament.'})
        self.assertThread(user1)

    def test_006_delete(self):
        while True:
            user1 = self.user()

            self.assertResponse(play(user1), 201)
            time.sleep(1)
            response = is_in_game(user1)
            if response.status_code == 404:
                break
            self.assertThread(user1)

        self.assertResponse(play(user1, method='DELETE'), 204)
        self.assertThread(user1)

    def test_006_delete_not_play(self):
        user1 = self.user()

        self.assertResponse(play(user1, method='DELETE'), 404, {'detail': 'You are not currently playing.'})
        self.assertThread(user1)

    def test_007_not_connected_sse(self):
        user1 = self.user(sse=False)

        self.assertResponse(play(user1), 401, {'code': 'sse_connection_required', 'detail': 'You need to be connected to SSE to access this resource.'})


if __name__ == '__main__':
    unittest.main()
