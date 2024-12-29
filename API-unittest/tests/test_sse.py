import time
import unittest

from services.auth import register_guest
from services.friend import friend_requests
from services.user import me
from utils.generate_random import rnstr
from utils.my_unittest import UnitTest


class Test01_SSE(UnitTest):

    def test_001_connection_success(self):
        user1 = self.new_user()

        thread1 = self.connect_to_sse(user1, tests=['connection-success'], ignore_connection_message=False)
        thread1.join()

    def test_002_connect_twice(self):
        user1 = self.new_user(get_me=True)
        user2 = self.new_user()

        thread1 = self.connect_to_sse(user1, ['connection-success'], ignore_connection_message=False)
        time.sleep(1)
        thread2 = self.connect_to_sse(user1, ['connection-success'], ignore_connection_message=False)
        thread1.join()
        self.assertResponse(friend_requests(user2, user1), 201)
        thread2.join()

    def test_003_invalid_token(self):
        thread1 = self.connect_to_sse({'token': 'invalid_token'}, status_code=401)
        thread1.join()

    def test_004_connection_success_guest(self):
        user1 = self.guest_user()

        thread1 = self.connect_to_sse(user1, tests=['connection-success'], ignore_connection_message=False)
        thread1.join()

    def test_005_guest_then_register(self):
        user1 = self.guest_user(get_me=True)
        username = 'sse-register-' + rnstr()

        thread1 = self.connect_to_sse(user1, tests=['connection-success'], ignore_connection_message=False)
        user1['username'] = self.assertResponse(register_guest(user1, username=username), 200, get_field='username')
        thread1.join()
        response = self.assertResponse(me(user1), 200)
        self.assertFalse(response['is_guest'])
        self.assertEqual(username, response['username'])

    def test_006_delete_user(self):
        user1 = self.user_sse()

        self.assertResponse(me(user1, 'DELETE', password=True), 204)
        user1['thread'].join()

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


if __name__ == '__main__':
    unittest.main()
