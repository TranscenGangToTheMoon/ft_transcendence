from services.blocked import blocked_user
from services.friend import create_friend, accept_friend_request, send_friend_request
from utils.credentials import new_user
from utils.my_unittest import UnitTest

# 1. todo make test
class Test01_Friend(UnitTest):

    def test_001_friend(self):
        self.assertFriendResponse(create_friend())

    def test_002_friend_without_friend_request(self):
        self.assertResponse(accept_friend_request(), 404, {'detail': 'Friend request not found.'})

    def test_003_friend_does_not_exist(self):
        self.assertResponse(accept_friend_request(sender={'username': 'caca'}), 404, {'detail': 'Friend request not found.'})

    def test_004_friend_already_friends(self):
        user1 = new_user()
        user2 = new_user()

        self.assertFriendResponse(create_friend(user1, user2))
        self.assertResponse(accept_friend_request(user2, user1), 409, {'detail': 'You are already friends with this user.'})

    def test_005_get_friends(self):
        user1 = new_user()

        for i in range(7):
            self.assertFriendResponse(create_friend(user1))

        response = accept_friend_request(user1, method='GET')
        self.assertResponse(response, 200)
        self.assertEqual(7, response.json['count'])


if __name__ == '__main__':
    unittest.main()
