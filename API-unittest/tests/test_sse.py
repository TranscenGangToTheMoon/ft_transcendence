import json
import unittest

from services.sse import notification
from services.user import me, get_user
from utils.credentials import new_user, guest_user, login
from utils.my_unittest import UnitTest


class Test01_SSE(UnitTest):
    pass

#todo message d'erreur qui finit pas un point
class Test02_Notification(UnitTest):

    def test_001_test_notification(self):
        with open('../user1.json') as f:
            user1 = json.load(f)

        user1 = self.assertResponse(login(user1['username'], user1['password']), 200, get_user=True)
        user1 = {**user1, **me(user1).json} # todo user token args
        # Thread(target=connect_to_sse, args=(user_1,)).start()
        # time.sleep(1)
        self.assertResponse(notification(user1, 'caca'), 201)


if __name__ == '__main__':
    unittest.main()
