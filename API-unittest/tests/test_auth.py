from services.auth import register
from utils.credentials import guest_user
from utils.generate_random import rnstr
from utils.my_unittest import UnitTest


# todo test login
# todo test login user does not exist
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


class Test02_RegisterGuest(UnitTest):

    def test_001_register_guest(self):
        guest = guest_user()

        # todo make get response
        user = {'token': self.assertResponse(register_guest(guest=guest), 200, get_id='access')}
        self.assertResponse(me(user), 200)

    def test_002_register_guest_without_tokent(self):
        random_name = rnstr()

        self.assertResponse(register_guest(username='username_' + random_name, password='password_,' + random_name), 401)

# todo try to register without tokent, without guest, alredy connected, etc...


if __name__ == '__main__':
    unittest.main()
