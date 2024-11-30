from services.blocked import blocked_user
from services.user import get_user, get_me
from utils.credentials import new_user
from utils.my_unittest import UnitTest


# todo test rename
# todo test rename invalid name
# todo test rename invalid name already exist
# todo test me

# todo test update user
# todo test get user friend field


class Test01_GetUsers(UnitTest):

    def test_001_get_user(self):
        self.assertResponse(get_user(), 200)

    def test_002_get_blocked_by_user(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(blocked_user(user2, user1['id']), 201)
        self.assertResponse(get_user(user1, user2['id']), 404, {'detail': 'User not found.'})

    def test_003_get_blocked_user(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(blocked_user(user1, user2['id']), 201)
        self.assertResponse(get_user(user1, user2['id']), 403, {'detail': 'You block this user.'})

    def test_004_get_user_doest_not_exist(self):
        self.assertResponse(get_user(user2_id=123456), 404, {'detail': 'User not found'})


if __name__ == '__main__':
    unittest.main()
