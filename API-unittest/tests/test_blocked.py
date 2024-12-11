import unittest
from random import randint

from services.blocked import are_blocked, blocked_user, unblocked_user
from utils.credentials import new_user, guest_user
from utils.my_unittest import UnitTest


class Test01_AreBlocked(UnitTest):

    def test_001_blocked(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(blocked_user(user1, user2['id']), 201)
        self.assertResponse(are_blocked(user1['id'], user2['id']), 200)
        self.assertResponse(are_blocked(user2['id'], user1['id']), 200)

    def test_002_not_blocked(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(are_blocked(user1['id'], user2['id']), 404, {'detail': 'Not found.'})
        self.assertResponse(are_blocked(user2['id'], user1['id']), 404, {'detail': 'Not found.'})


class Test02_Blocked(UnitTest):

    def test_001_blocked(self):
        user1 = new_user()

        n = randint(1, 10)
        for _ in range(n):
            self.assertResponse(blocked_user(user1), 201)
        self.assertResponse(blocked_user(user1, method='GET'), 200, count=n)

    def test_002_unblocked(self):
        user1 = new_user()
        user2 = new_user()

        block_id = self.assertResponse(blocked_user(user1, user2['id']), 201, get_field=True)
        self.assertResponse(blocked_user(user1, method='GET'), 200, count=1)
        self.assertResponse(unblocked_user(user1, block_id), 204)
        self.assertResponse(blocked_user(user1, method='GET'), 200, count=0)


class Test03_BlockedError(UnitTest):

    def test_001_already_blocked(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(blocked_user(user1, user2['id']), 201)
        self.assertResponse(blocked_user(user1, user2['id']), 409, {'detail': 'You are already blocked this user.'})

    def test_002_blocked_not_existing_user(self):
        user1 = new_user()

        self.assertResponse(blocked_user(user1, 123456), 404, {'detail': 'User not found.'})

    def test_003_blocked_user_that_block_us(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(blocked_user(user1, user2['id']), 201)
        self.assertResponse(blocked_user(user2, user1['id']), 404, {'detail': 'User not found.'})

    def test_004_blocked_guest(self):
        user1 = new_user()
        user2 = guest_user()

        self.assertResponse(blocked_user(user1, user2['id']), 404, {'detail': 'User not found.'})

    def test_005_blocked_by_guest(self):
        user1 = guest_user()
        user2 = new_user()

        self.assertResponse(blocked_user(user1, user2['id']), 403, {'detail': 'Guest users cannot blocked users.'})

    def test_006_unblock_doest_not_exist(self):
        self.assertResponse(unblocked_user(new_user(), 123456), 403, {'detail': 'This blocked user entry does not belong to you.'})

    def test_007_unblock_not_self_instance(self):
        block_id = self.assertResponse(blocked_user(new_user()), 201, get_field=True)
        self.assertResponse(unblocked_user(new_user(), block_id), 403, {'detail': 'This blocked user entry does not belong to you.'})


if __name__ == '__main__':
    unittest.main()
