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

        self.assertResponse(register(username, password), 201)

class Test02_RegisterGuest(UnitTest):

    def test_001_register_guest(self):
        guest = guest_user()
        print(guest, flush=True)

        self.assertResponse(register(guest=guest, method='PATCH'), 200)

# todo try to register without tokent, without guest, alredy connected, etc...


if __name__ == '__main__':
    unittest.main()
