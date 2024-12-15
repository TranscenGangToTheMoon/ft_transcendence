import unittest

from services.auth import register, register_guest
from services.play import play
from services.user import me
from utils.credentials import guest_user, new_user, login, auth_guest
from utils.generate_random import rnstr
from utils.my_unittest import UnitTest


# todo test refresh

class Test01_Register(UnitTest):

    def test_001_register(self):
        username = 'register_test' + rnstr()
        password = 'password_' + username

        response = self.assertResponse(register(username, password), 201)
        user = {'token': response['access']}
        self.assertResponse(me(user), 200)
        self.assertResponse(login(username, password), 200)

    def test_002_register_already_exist(self):
        user1 = new_user()

        self.assertResponse(register(user1['username'], user1['password']), 400)
        self.assertResponse(register(user1['username'].upper(), user1['password']), 400)

    def test_003_register_invalid_username(self):
        usernames = [
            'de',
            'username_too_long_because_its_must_be_short',
            'invalid_char!@#$',
            'admin',
            'staff',
            'support',
            'ft_transcendence',
            'transcendence',
            'anonymus',
            '',
        ]
        password = 'InvalideUser_123' + rnstr()

        for username in usernames:
            self.assertResponse(register(username, password), 400)

    def test_004_register_invalid_password(self):
        username = 'register_inv_password' + rnstr()
        passwords = [
            '!$@^Invalid_char123',
            'Contain_username1' + username,
            'min_len',
            'no_upper_case123',
            'NO_LOWER_CASE123',
            'NoSpecialChar123',
            'NoNumbers',
            '123456',
            'password',
            'azerty',
            'qwerty',
            'aaaaaaaa',
            '123456789',
            'abcdefg',
            ''
        ]

        for password in passwords:
            self.assertResponse(register(username, password), 400)


class Test02_Guest(UnitTest):

    def test_001_create_guest(self):
        self.assertResponse(auth_guest(), 201)

    def test_002_register_guest(self):
        guest = guest_user()
        username = 'guest-register' + rnstr()

        # todo make get response
        user = {'token': self.assertResponse(register_guest(username=username, guest=guest), 200, get_field='access')} #todo make truc pour avoir le bon token
        test_username = self.assertResponse(me(user), 200, get_field='username') # todo rename get id get field
        self.assertEquals(username, test_username)

    def test_003_register_guest_without_tokent(self):
        random_name = rnstr()

        self.assertResponse(register_guest(username='username_' + random_name, password='password_,' + random_name), 401)

    def test_004_register_user_since_guest(self):
        self.assertResponse(register_guest(guest=new_user()), 403)  # todo add json response test

    def test_005_login_guest(self):
        self.assertResponse(login(guest_user()['username'], rnstr()), 401, {'detail': 'No active account found with the given credentials'})

    def test_006_register_guest_try_play_ranked(self):
        guest = guest_user()

        self.assertResponse(play(guest, 'ranked'), 403, {'detail': 'Guest users cannot play ranked games.'})
        user = {'token': self.assertResponse(register_guest(guest=guest), 200, get_field='access')}
        self.assertResponse(play(user, 'ranked'), 201)


class Test03_Login(UnitTest):

    def test_001_login_user_doest_not_exist(self):
        user1 = new_user()

        self.assertResponse(login(user1['username'], user1['password']), 200)

    def test_002_login_bad_password(self):
        self.assertResponse(login('caca', 'pipi'), 401, {'detail': 'No active account found with the given credentials'})

    def test_003_invalid_password(self):
        user1 = new_user()

        self.assertResponse(login(user1['username'], 'zizi'), 401, {'detail': 'No active account found with the given credentials'})

    def test_004_missing_field(self):
        user1 = new_user()

        self.assertResponse(login(data={}), 400, {'username': ['This field is required.'], 'password': ['This field is required.']})


if __name__ == '__main__':
    unittest.main()
