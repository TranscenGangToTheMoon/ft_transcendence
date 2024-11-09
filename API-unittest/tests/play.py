import unittest

from services.lobby import create_lobby, join_lobby
from services.play import play
from utils.credentials import new_user, guest_user
from utils.unittest import UnitTest


class Test01_Play(UnitTest):

    def test_001_play_duel(self):
        self.assertResponse(play(), 201)

    def test_001_play_ranked(self):
        self.assertResponse(play(game_mode='ranked'), 201)


class Test02_PlayError(UnitTest):

    def test_001_already_in_game(self):
        self.assertResponse(play(), 201)
        self.assertResponse(play(), 201) # todo ??

    def test_002_already_in_tournament(self):
        # self.assertResponse(create_tournament(), create_tournament201)
        self.assertResponse(play(), 201)

    def test_003_guest_cannot_play_ranked(self):
        self.assertResponse(play(guest_user(), 'ranked'), 403, {'detail': 'Guest users cannot play ranked games.'})

    def test_004_user_in_lobby(self):
        user1 = new_user()

        self.assertResponse(create_lobby(user1), 201)
        self.assertResponse(play(user1), 201)

        response = create_lobby(user1, method='GET')
        self.assertResponse(response, 200, {'detail': 'You are not in any lobby.'})
        code = response.json['code']

        self.assertResponse(join_lobby(code, user1, 'GET'), 404, {'detail': 'Lobby not found.'})

    # def test_004_user_in_tournament(self): todo
    #     user1 = new_user()
    #
    #     self.assertResponse(create_lobby(user1), 200)
    #     self.assertResponse(play(user1), 201)
    #     response = create_lobby(user1, method='GET')
    #     self.assertResponse(response, 200, {'detail': 'You are not in any lobby.'})
    #     code = response.json['code']
    #     self.assertResponse(join_lobby(code, user1, 'GET'), 404, {'detail': 'Lobby not found.'})


if __name__ == '__main__':
    unittest.main()
