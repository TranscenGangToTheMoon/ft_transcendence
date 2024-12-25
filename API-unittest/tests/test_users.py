import time
import unittest

from services.auth import login
from services.blocked import blocked_user
from services.chat import create_chat, accept_chat, request_chat_id
from services.friend import friend_requests, get_friend_requests_received, create_friendship, friend, get_friends, \
    friend_request
from services.game import create_game, is_in_game
from services.lobby import create_lobby, join_lobby
from services.play import play
from services.tournament import create_tournament, search_tournament, join_tournament
from services.user import get_user, me
from utils.generate_random import rnstr
from utils.my_unittest import UnitTest


# todo test update user
# todo test get friend field
# todo test get status field


class Test01_GetUsers(UnitTest):

    def test_001_get_user(self):
        user1 = self.new_user()
        user2 = self.new_user(get_me=True)

        self.assertResponse(get_user(user1, user2['id']), 200)

    def test_002_get_blocked_by_user(self):
        user1 = self.new_user(get_me=True)
        user2 = self.new_user(get_me=True)

        self.assertResponse(blocked_user(user2, user1['id']), 201)
        self.assertResponse(get_user(user1, user2['id']), 404, {'detail': 'User not found.'})

    def test_003_get_blocked_user(self):
        user1 = self.new_user()
        user2 = self.new_user(get_me=True)

        self.assertResponse(blocked_user(user1, user2['id']), 201)
        self.assertResponse(get_user(user1, user2['id']), 403, {'detail': 'You blocked this user.'})

    def test_004_get_user_doest_not_exist(self):
        user1 = self.new_user()

        self.assertResponse(get_user(user1, user2_id=123456), 404, {'detail': 'User not found.'})


class Test02_UserMe(UnitTest):

    def test_001_get_me(self):
        user1 = self.new_user(connect_sse=True)

        response = self.assertResponse(me(user1), 200)
        self.assertDictEqual(response, {'id': response['id'], 'username': user1['username'], 'is_guest': False, 'created_at': response['created_at'], 'profile_picture': None, 'accept_friend_request': True, 'accept_chat_from': 'friends_only', 'coins': 100, 'trophies': 0, 'current_rank': None, 'friend_notifications': 0, 'is_online': True})

    def test_002_get_me_guest(self):
        user1 = self.guest_user(connect_sse=True)

        response = self.assertResponse(me(user1), 200)
        self.assertDictEqual(response, {'id': response['id'], 'username': response['username'], 'is_guest': True, 'created_at': response['created_at'], 'profile_picture': None, 'accept_friend_request': True, 'accept_chat_from': 'friends_only', 'coins': 100, 'trophies': 0, 'current_rank': None, 'friend_notifications': 0, 'is_online': True})


class Test03_DeleteUser(UnitTest):

    def test_001_delete(self):
        user1 = self.new_user()

        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(me(user1), 401, {'detail': 'Incorrect authentication credentials.'})

    def test_002_delete_not_get_me(self):
        user1 = self.new_user()

        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(me(user1), 401, {'detail': 'Incorrect authentication credentials.'})

    def test_003_already_delete(self):
        user1 = self.new_user()

        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(me(user1, method='DELETE', password=True), 401, {'detail': 'Incorrect authentication credentials.'})

    def test_004_request_after_delete(self):
        user1 = self.new_user()

        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(create_lobby(user1), 401, {'detail': 'Incorrect authentication credentials.'})

    def test_005_user_in_lobby(self):
        user1 = self.new_user()
        user2 = self.new_user()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')
        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(create_lobby(user1, method='GET'), 401, {'detail': 'Incorrect authentication credentials.'})
        self.assertResponse(join_lobby(user2, code), 404, {'detail': 'Lobby not found.'})

    def test_006_user_in_game(self):
        user1 = self.new_user()
        user2 = self.new_user()

        self.assertResponse(create_game(user1, user2), 201)
        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        # todo make when have game

    def test_007_user_in_tournament(self):
        user1 = self.new_user()
        user2 = self.new_user()
        user3 = self.new_user()
        name = rnstr()

        code = self.assertResponse(create_tournament(user1, {'name': 'Delete User ' + name}), 201, get_field='code')
        self.assertResponse(search_tournament(user2, name), 200, count=1)
        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(create_tournament(user1, method='GET'), 401, {'detail': 'Incorrect authentication credentials.'})
        self.assertResponse(search_tournament(user2, name), 200, count=0)
        self.assertResponse(join_tournament(user3, code), 404)

    def test_008_user_in_start_tournament(self):
        user1 = self.new_user()
        user2 = self.new_user()
        user3 = self.new_user()
        name = rnstr()

        code = self.assertResponse(create_tournament(user1, {'name': 'Delete User ' + name}), 201, get_field='code')
        self.assertResponse(join_tournament(user2, code), 201)
        response = self.assertResponse(search_tournament(user3, name), 200, count=1)
        self.assertEqual(2, response['results'][0]['n_participants'])
        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        response = self.assertResponse(search_tournament(user3, name), 200, count=1)
        self.assertEqual(1, response['results'][0]['n_participants'])
        # todo make when tournament work

    def test_009_chat_with(self):
        user1 = self.new_user()
        user2 = self.new_user()

        self.assertResponse(accept_chat(user2), 200)
        chat_id = self.assertResponse(create_chat(user1, user2['username']), 201, get_field=True)
        self.assertResponse(request_chat_id(user2, chat_id), 200)
        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(request_chat_id(user2, chat_id), 403, {'detail': 'You do not belong to this chat.'})

    def test_010_play_duel(self):
        user2 = self.new_user()

        while True:
            user1 = self.new_user()

            self.assertResponse(play(user1), 201)
            time.sleep(1)
            response = is_in_game(user1)
            if response.status_code == 404:
                break
        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(play(user2), 201)
        time.sleep(1)
        self.assertResponse(is_in_game(user2), 404, {'detail': 'This user is not in a game.'})

    def test_012_play_ranked(self):
        user2 = self.new_user()

        while True:
            user1 = self.new_user()

            self.assertResponse(play(user1, 'ranked'), 201)
            time.sleep(1)
            response = is_in_game(user1)
            if response.status_code == 404:
                break
        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(play(user2, 'ranked'), 201)
        time.sleep(1)
        self.assertResponse(is_in_game(user2), 404, {'detail': 'This user is not in a game.'})

    def test_013_friend_request(self):
        user1 = self.new_user()
        user2 = self.new_user()

        friend_request_id = self.assertResponse(friend_requests(user1, user2), 201, get_field=True)
        self.assertResponse(get_friend_requests_received(user2), 200, count=1)
        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(friend_request(friend_request_id, user2, 'GET'), 404)
        self.assertResponse(get_friend_requests_received(user2), 200, count=0)

    def test_014_friend(self):
        user1 = self.new_user()
        user2 = self.new_user()
        user3 = self.new_user()

        id = self.assertFriendResponse(create_friendship(user1, user2))
        self.assertFriendResponse(create_friendship(user1, user3))
        self.assertResponse(friend(user2, id), 200)
        self.assertResponse(get_friends(user1), 200, count=2)
        self.assertResponse(get_friends(user2), 200, count=1)
        self.assertResponse(get_friends(user3), 200, count=1)
        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(friend(user2, id), 404, {'detail': 'Friendship not found.'})
        self.assertResponse(get_friends(user2), 200, count=0)
        self.assertResponse(get_friends(user3), 200, count=0)

    def test_015_blocked(self):
        user1 = self.new_user()
        user2 = self.new_user()

        self.assertResponse(blocked_user(user2, user1['id']), 201)
        self.assertResponse(blocked_user(user2, user1['id'], method='GET'), 200, count=1)
        self.assertResponse(me(user1, method='DELETE', password=True), 204)
        self.assertResponse(blocked_user(user2, user1['id'], method='GET'), 200, count=0)


class Test04_UpdateUserMe(UnitTest):

    def test_001_update_password(self):
        user1 = self.new_user()
        old_password = user1['password']

        self.assertResponse(me(user1, method='PATCH', data={'password': 'new_password'}), 200)
        self.assertResponse(login(user1['username'], 'new_password'), 200)
        self.assertResponse(login(user1['username'], old_password), 401, {'detail': 'No active account found with the given credentials'})

    def test_002_update_password_same_as_before(self):
        user1 = self.new_user()

        self.assertResponse(me(user1, method='PATCH', data={'password': user1['password']}), 400, {'password': ['Password is the same as the old one.']})
        self.assertResponse(login(data=user1), 200)


class Test05_RenameUser(UnitTest):

    def test_001_rename_user(self):
        user1 = self.new_user()
        old_username = user1['username']
        new_username = old_username + '_new'

        self.assertResponse(me(user1, method='PATCH', data={'username': new_username}), 200)
        self.assertResponse(login(new_username, user1['password']), 200)
        self.assertResponse(login(old_username, user1['password']), 401, {'detail': 'No active account found with the given credentials'})

    def test_002_rename_user_friend(self):
        user1 = self.new_user()
        user2 = self.new_user()
        new_username = user1['username'] + '_new'

        id = self.assertFriendResponse(create_friendship(user1, user2))
        user1['id'] = self.assertResponse(me(user1, method='PATCH', data={'username': new_username}), 200, get_field=True)
        response = self.assertResponse(friend(user1, id), 200)
        for f in response['friends']:
            if f['id'] == user1['id']:
                self.assertEqual(new_username, f['username'])
                break

    def test_003_rename_blocked_user(self):
        user1 = self.new_user(get_me=True)
        user2 = self.new_user()
        new_username = user1['username'] + '_new'

        self.assertResponse(blocked_user(user2, user1['id']), 201)
        self.assertResponse(me(user1, method='PATCH', data={'username': new_username}), 200)

        response = self.assertResponse(blocked_user(user2, method='GET'), 200, count=1)
        self.assertEqual(response['results'][0]['blocked']['username'], new_username)

    def test_004_rename_chat(self):
        old_username = 'rename-chat-' + rnstr()
        user1 = self.new_user(username=old_username)
        user2 = self.new_user()
        new_username = 'new-username-' + rnstr()

        self.assertResponse(accept_chat(user2), 200)
        self.assertResponse(create_chat(user1, user2['username']), 201)
        self.assertResponse(me(user1, method='PATCH', data={'username': new_username}), 200)

        self.assertResponse(create_chat(user2, method='GET', data={'q': old_username}), 200, count=0)
        self.assertResponse(create_chat(user2, method='GET', data={'q': new_username}), 200, count=1)


if __name__ == '__main__':
    unittest.main()
