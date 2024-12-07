import unittest

from services.auth import register, register_guest
from services.user import me
from utils.credentials import guest_user, new_user, login, auth_guest
from utils.generate_random import rnstr
from utils.my_unittest import UnitTest


# todo test login user bad password
# todo test register
# todo test register invalid name
# todo test register invalid password
# todo test refresh
# todo test get token
# todo test guest

class Test01_Register(UnitTest):

    def test_001_register(self):
        username = 'register_test' + rnstr()
        password = 'password_' + username

        response = register(username, password)
        user = {'token': response.json['access']}
        self.assertResponse(response, 201)
        self.assertResponse(me(user), 200)
        self.assertResponse(login(username, password), 200)

    def test_002_register_already_exist(self):
        user1 = new_user()

        self.assertResponse(register(user1['username'], user1['password']), 400)


class Test02_RegisterGuest(UnitTest):

    def test_001_register_guest(self):
        guest = guest_user()

        # todo make get response
        user = {'token': self.assertResponse(register_guest(guest=guest), 200, get_id='access')}
        self.assertResponse(me(user), 200)

    def test_002_register_guest_without_tokent(self):
        random_name = rnstr()

        self.assertResponse(register_guest(username='username_' + random_name, password='password_,' + random_name), 401)

    def test_003_register_user_since_guest(self):
        self.assertResponse(register_guest(guest=new_user()), 403)  # todo add json response test

class Test03_Login(UnitTest):

    def test_001_login_user_doest_not_exist(self):
        user1 = new_user()

        self.assertResponse(login(user1['username'], user1['password']), 200)


if __name__ == '__main__':
    unittest.main()
