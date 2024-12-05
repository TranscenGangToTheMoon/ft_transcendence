import time

from services.blocked import blocked_user
from services.chat import create_chat, accept_chat, request_chat_id
from services.game import create_game, is_in_game
from services.lobby import create_lobby, join_lobby
from services.play import play
from services.tournament import create_tournament, search_tournament, join_tournament
from services.user import get_user, me
from utils.credentials import new_user, get_token
from utils.generate_random import rnstr
from utils.my_unittest import UnitTest


# todo test rename
# todo test rename invalid name
# todo test rename invalid name already exist

# todo test update user
# todo test get user friend field
# todo test get status field


class Test01_GetUsers(UnitTest):

    def test_001_get_user(self):
        self.assertResponse(get_user(), 200)

    def test_002_get_blocked_by_user(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(blocked_user(user2, user1['id']), 201)
        self.assertResponse(get_user(user1, user2['id']), 404, {'detail': 'User not found.'})

    def test_003_get_blocked_user(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(blocked_user(user1, user2['id']), 201)
        self.assertResponse(get_user(user1, user2['id']), 403, {'detail': 'You blocked this user.'})

    def test_004_get_user_doest_not_exist(self):
        self.assertResponse(get_user(user2_id=123456), 404, {'detail': 'User not found.'})


class Test02_UserMe(UnitTest):

    def test_001_get_me(self):
        user1 = new_user()

        response = me(user1)
        self.assertResponse(response, 200)
        self.assertDictEqual(response.json, {'id': user1['id'], 'username': user1['username'], 'is_guest': False, 'created_at': response.json['created_at'], 'profile_picture': None, 'accept_friend_request': True, 'accept_chat_from': 'friends_only', 'coins': 100, 'trophies': 0, 'current_rank': None})


class Test03_DeleteUser(UnitTest):

    def test_001_delete(self):
        user1 = new_user()

        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(me(user1), 404, {'detail': 'User not found.'})

    def test_002_delete_not_get_me(self):
        user1 = new_user(get_me=False)

        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(me(user1), 404, {'detail': 'User not found.'})

    def test_003_already_delete(self):
        user1 = new_user()

        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(me(user1, method='DELETE', password=True), 404, {'detail': 'User not found.'})

    def test_004_request_after_delete(self):
        user1 = new_user()

        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(create_lobby(user1), 404, {'detail': 'User not found.'})

    def test_005_user_in_lobby(self):
        user1 = new_user()

        code = self.assertResponse(create_lobby(user1), 201, get_id='code')
        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(create_lobby(user1, method='GET'), 401, {'detail': 'Invalid token.'})
        self.assertResponse(join_lobby(code), 404, {'detail': 'User not found.'})

    def test_006_user_in_game(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(create_game(user1, user2), 201)
        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        # todo make when have game

    def test_007_user_in_tournament(self):
        user1 = new_user()
        name = rnstr()

        code = self.assertResponse(create_tournament(user1, {'name': 'Delete User ' + name}), 201, get_id='code')
        self.assertResponse(join_tournament(code), 201)
        self.assertResponse(search_tournament(name), 200, count=1)
        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(create_tournament(user1, method='GET'), 401, {'detail': 'Invalid token.'})
        self.assertResponse(search_tournament(name), 200, count=0)

    def test_008_user_in_start_tournament(self):
        user1 = new_user()
        name = rnstr()

        code = self.assertResponse(create_tournament(user1, {'name': 'Delete User ' + name}), 201, get_id='code')
        self.assertResponse(join_tournament(code), 201)
        self.assertResponse(search_tournament(name), 200, count=1)
        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(create_tournament(user1, method='GET'), 401, {'detail': 'Invalid token.'})
        self.assertResponse(search_tournament(name), 200, count=0)
        # todo make when tournament work

    def test_009_chat_with(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(accept_chat(user2), 201)
        chat_id = self.assertResponse(create_chat(user1, user2), 201, get_id=True)
        self.assertResponse(request_chat_id(user2, chat_id), 201)
        self.assertResponse(me(user1, method='DELETE', data={'password': user2['password']}), 201)
        self.assertResponse(request_chat_id(user2, chat_id), 404, {'detail': 'You do not belong to this chat.'})

    def test_010_play_duel(self):
        user2 = new_user()

        while True:
            user1 = new_user()

            self.assertResponse(play(user1), 201)
            time.sleep(1)
            response = is_in_game(user1)
            if response.status_code == 404:
                break
        self.assertResponse(me(user1, method='DELETE', data={'password': user2['password']}), 201)
        self.assertResponse(play(user2), 201)
        self.assertResponse(is_in_game(user2), 404, {'detail': 'User not found.'})

    def test_012_play_ranked(self):
        user2 = new_user()

        while True:
            user1 = new_user()

            self.assertResponse(play(user1, 'ranked'), 201)
            time.sleep(1)
            response = is_in_game(user1)
            if response.status_code == 404:
                break
        self.assertResponse(me(user1, method='DELETE', data={'password': user2['password']}), 201)
        self.assertResponse(play(user2, 'ranked'), 201)
        time.sleep(1)
        self.assertResponse(is_in_game(user2), 404, {'detail': 'User not found.'})


if __name__ == '__main__':
    unittest.main()
