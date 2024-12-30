import time
import unittest

from services.auth import register_guest
from services.friend import friend_requests
from services.lobby import create_lobby, join_lobby
from services.user import me
from utils.generate_random import rnstr
from utils.my_unittest import UnitTest


class Test01_SSE(UnitTest):

    def test_001_connection_success(self):
        user1 = self.user()

        self.assertThread(user1)

    def test_002_guest_connection_success(self):
        user1 = self.user(guest=True)

        self.assertThread(user1)

    def test_003_connect_twice(self):
        user1 = self.user()
        user2 = self.user()
        user3 = self.user()

        user1_bis = user1.copy()
        self.connect_to_sse(user1, ['receive-friend-request'])
        time.sleep(1)
        self.connect_to_sse(user1_bis, ['receive-friend-request', 'receive-friend-request'])

        self.assertResponse(friend_requests(user2, user1), 201)
        self.assertThread(user1)
        self.assertResponse(friend_requests(user3, user1), 201)
        self.assertThread(user1_bis)

    def test_004_invalid_token(self):
        thread1 = self.connect_to_sse({'token': 'invalid_token'}, status_code=401)
        thread1.join()

    def test_005_guest_then_register(self):
        user1 = self.user(guest=True)
        username = 'sse-register-' + rnstr()

        self.assertResponse(register_guest(user1, username=username), 200)
        user1['username'] = username
        self.assertThread(user1)
        response = self.assertResponse(me(user1), 200)
        self.assertFalse(response['is_guest'])
        self.assertEqual(username, response['username'])

    def test_006_delete_user(self):
        user1 = self.user()

        self.assertResponse(me(user1, 'DELETE', password=True), 204)
        self.assertThread(user1)

#todo message d'erreur qui finit pas un point
#todo test invalid parameters, fogrt, not good type, etc..., not users.
# class Test02_EventsEndpoint(UnitTest):
#
#     def test_001_test_message(self):
#         # with open('../user1.json') as f:
#         #     user1 = json.load(f)
#         #
#         # user1 = self.assertResponse(login(user1['username'], user1['password']), 200, get_user=True)
#         # user1 = {**user1, **me(user1).json} # todo user token args
#         # Thread(target=connect_to_sse, args=(user_1,)).start()
#         # time.sleep(1)
#         users = [int(i) for i in input('users -> ').split(' ')]
#         self.assertResponse(events(users=users, data={'caca': 'pipi'}), 201)


class Test03_SSEConnectionClose(UnitTest):

    def test_001_last_online(self):
        user1 = self.user()
        user2 = self.user()

        last_online = self.assertResponse(me(user1), 200, get_field='last_online')
        time.sleep(0.5)
        self.assertThread(user1)
        time.sleep(0.5)
        response = self.assertResponse(friend_requests(user2, user1), 201)
        self.assertNotEqual('online', response['receiver']['status'])
        self.assertNotEqual(last_online, response['receiver']['status'])
        self.assertThread(user2)

    def test_002_leave_lobby_when_disconnect(self):
        user1 = self.user(['lobby-join'])
        user2 = self.user(['lobby-leave', 'lobby-update-participant'])

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')
        self.assertResponse(join_lobby(user2, code), 201)
        self.assertThread(user1)
        time.sleep(1)
        self.assertThread(user2)


if __name__ == '__main__':
    unittest.main()
