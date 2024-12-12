import unittest

import pyperclip

from services.sse import notification, connect_to_sse
from services.user import me
from utils.credentials import new_user, guest_user, login
from utils.my_unittest import UnitTest


class Test01_SSE(UnitTest):
    pass


class Test02_Notification(UnitTest):

    def test_001_test_notification(self):
        username, password = pyperclip.paste().split(' ')
        print(username, password)
        user1 = {'token': login(username, password).json['access']}
        user1 = {**user1, **me(user1).json} # todo user token args
        # Thread(target=connect_to_sse, args=(user_1,)).start()
        # time.sleep(1)
        self.assertResponse(notification(user1, 'caca'), 201)


if __name__ == '__main__':
    unittest.main()
