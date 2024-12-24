import time
import unittest

from utils.my_unittest import UnitTest


class Test01_SSE(UnitTest):

    def test_001_connection_success(self):
        user1 = self.new_user()
        user2 = self.guest_user()

        thread1 = self.connect_to_sse(user1, tests=[{'service': 'auth', 'event_code': 'connection-success'}], ignore_connection_message=False)
        thread2 = self.connect_to_sse(user2, tests=[{'service': 'auth', 'event_code': 'connection-success'}], ignore_connection_message=False)
        thread1.join()
        thread2.join()

    def test_002_connect_twice(self):
        user1 = self.new_user()

        thread1 = self.connect_to_sse(user1, [{'service': 'auth', 'event_code': 'connection-success'}], 3, ignore_connection_message=False)
        time.sleep(1)
        thread2 = self.connect_to_sse(user1, timeout=2, status_code=409)
        thread1.join()
        thread2.join()

    def test_003_invalid_token(self):
        thread1 = self.connect_to_sse({'token': 'invalid_token'}, status_code=401)
        thread1.join()


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
