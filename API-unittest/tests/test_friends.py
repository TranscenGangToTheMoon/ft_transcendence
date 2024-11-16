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

        self.assertResponse(accept_friend_request(user1, method='GET'), 200, count=7)

    def test_006_friends_then_block(self):
        user1 = new_user()
        user2 = new_user()

        self.assertFriendResponse(create_friend(user1, user2))
        self.assertResponse(accept_friend_request(user2, method='GET'), 200, count=1)

        self.assertResponse(blocked_user(user1, user2['username']), 201)

        for u in (user1, user2):
            self.assertResponse(accept_friend_request(u, method='GET'), 200, count=0)

    def test_007_no_field_username(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(send_friend_request(user1, user2), 201)

        response = accept_friend_request(user1, data={})
        self.assertResponse(response, 400, {'username': ['This field is required.']})


class Test02_FriendRequest(UnitTest):

    def test_001_friend_request(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(send_friend_request(user1, user2), 201)
        self.assertResponse(receive_friend_requests(user2), 200, count=1)
        self.assertResponse(send_friend_request(user1, method='GET'), 200, count=1)

    def test_002_user_does_not_exist(self):
        user1 = new_user()

        self.assertResponse(send_friend_request(user1, {'username': 'caca'}), 404, {'detail': 'User not found.'})

    def test_003_already_request(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(send_friend_request(user1, user2), 201)
        self.assertResponse(send_friend_request(user1, method='GET'), 409, {'detail': 'You already send a friend requests to this user.'})


if __name__ == '__main__':
    unittest.main()
