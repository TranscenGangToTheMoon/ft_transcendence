import unittest

from services.blocked import blocked_user
from services.friend import create_friendship, friend_request, friend_requests, get_friend_requests_received, \
    get_friends, friend
from utils.credentials import new_user
from utils.my_unittest import UnitTest


class Test01_Friend(UnitTest):

    def test_001_friend(self):
        self.assertFriendResponse(create_friendship())

    def test_002_friend_without_friend_request(self):
        self.assertResponse(friend_request('123456'), 404, {'detail': 'Friend request not found.'})

    def test_003_get_friends(self):
        user1 = new_user()

        for i in range(7):
            self.assertFriendResponse(create_friendship(user1))

        self.assertResponse(get_friends(user1), 200, count=7)

    def test_004_friends_then_block(self):
        user1 = new_user()
        user2 = new_user()

        self.assertFriendResponse(create_friendship(user1, user2))
        self.assertResponse(get_friends(user2), 200, count=1)

        self.assertResponse(blocked_user(user1, user2['id']), 201)

        for u in (user1, user2):
            self.assertResponse(get_friends(u), 200, count=0)

    def test_005_delete_friend_user1(self):
        user1 = new_user()
        user2 = new_user()

        friendship_id = self.assertFriendResponse(create_friendship(user1, user2))
        self.assertResponse(friend(user1, friendship_id), 200)
        self.assertResponse(friend(user1, friendship_id, 'DELETE'), 204)

        self.assertResponse(friend(user1, friendship_id), 404, {'detail': 'Friendship not found.'})
        self.assertResponse(get_friends(user2), 200, count=0)

    def test_006_delete_friend_user2(self):
        user1 = new_user()
        user2 = new_user()

        friendship_id = self.assertFriendResponse(create_friendship(user1, user2))
        self.assertResponse(friend(user1, friendship_id), 200)
        self.assertResponse(friend(user2, friendship_id, 'DELETE'), 204)

        self.assertResponse(friend(user2, friendship_id), 404, {'detail': 'Friendship not found.'})
        self.assertResponse(get_friends(user1), 200, count=0)

    def test_007_delete_friend_not_belon_user(self):
        user1 = new_user()
        user2 = new_user()

        friendship_id = self.assertFriendResponse(create_friendship(user1, user2))
        self.assertResponse(friend(user1, friendship_id), 200)

        self.assertResponse(friend(new_user(), friendship_id, 'DELETE'), 404, {'detail': 'Friendship not found.'})
        self.assertResponse(friend(user1, friendship_id), 200)


class Test02_FriendRequest(UnitTest):

    def test_001_friend_request(self):
        user1 = new_user()
        user2 = new_user()

        friend_request_id = self.assertResponse(friend_requests(user1, user2), 201, get_id=True)

        self.assertResponse(get_friend_requests_received(user2), 200, count=1)
        self.assertResponse(friend_requests(user1, method='GET'), 200, count=1)
        self.assertResponse(friend_request(friend_request_id, user1, method='GET'), 200)
        self.assertResponse(friend_request(friend_request_id, user2, method='GET'), 200)

    def test_002_user_does_not_exist(self):
        user1 = new_user()

        self.assertResponse(friend_requests(user1, {'username': 'caca'}), 404, {'detail': 'User not found.'})

    def test_003_already_request(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(friend_requests(user1, user2), 201)
        self.assertResponse(friend_requests(user1, user2), 409, {'detail': 'You have already sent a friend request to this user.'})
        self.assertResponse(friend_requests(user2, user1), 409, {'detail': 'You have already received a friend request from this user.'})

    def test_004_already_friends(self):
        user1 = new_user()
        user2 = new_user()

        self.assertFriendResponse(create_friendship(user1, user2))
        self.assertResponse(friend_requests(user1, user2), 409, {'detail': 'You are already friends with this user.'})

    def test_005_send_friend_request_then_blocked(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(friend_requests(user1, user2), 201)
        self.assertResponse(blocked_user(user2, user1['id']), 201)
        self.assertResponse(get_friend_requests_received(user2), 200, count=0)
        self.assertResponse(friend_requests(user1, method='GET'), 200, count=0)

    def test_006_blocked_then_send_friend_request(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(blocked_user(user1, user2['id']), 201)
        self.assertResponse(friend_requests(user1, user2), 403, {'detail': 'You blocked this user.'})
        self.assertResponse(friend_requests(user2, user1), 404, {'detail': 'User not found.'})

    def test_007_send_friend_request_to_myself(self):
        user1 = new_user()

        self.assertResponse(friend_requests(user1, user1), 403, {'detail': 'You cannot send a friend request to yourself.'})

    def test_008_forget_username_field(self):
        self.assertResponse(friend_requests(data={}), 400, {'username': ['This field is required.']})

    def test_009_get_friend_request_not_belong(self):
        user1 = new_user()
        user2 = new_user()

        friend_request_id = self.assertResponse(friend_requests(user1, user2), 201, get_id=True)

        self.assertResponse(friend_request(friend_request_id), 404, {'detail': 'Friend request not found.'})

    def test_010_reject_friend_request(self):
        user1 = new_user()
        user2 = new_user()

        friend_request_id = self.assertResponse(friend_requests(user1, user2), 201, get_id=True)

        self.assertResponse(friend_request(friend_request_id, user2, 'DELETE'), 204)
        self.assertResponse(friend_request(friend_request_id, user1, 'GET'), 404, {'detail': 'Friend request not found.'})

    def test_011_cancel_friend_request(self):
        user1 = new_user()
        user2 = new_user()

        friend_request_id = self.assertResponse(friend_requests(user1, user2), 201, get_id=True)

        self.assertResponse(friend_request(friend_request_id, user1, 'DELETE'), 204)
        self.assertResponse(friend_request(friend_request_id, user1, 'GET'), 404, {'detail': 'Friend request not found.'})
        self.assertResponse(friend_request(friend_request_id, user2, 'GET'), 404, {'detail': 'Friend request not found.'})

    def test_012_delete_friend_request_after_became_friend(self):
        user1 = new_user()
        user2 = new_user()

        friend_request_id = self.assertResponse(friend_requests(user1, user2), 201, get_id=True)
        self.assertResponse(friend_request(friend_request_id, user2), 201, get_id=True)
        self.assertResponse(friend_request(friend_request_id, user1, 'GET'), 404, {'detail': 'Friend request not found.'})
        self.assertResponse(friend_request(friend_request_id, user2, 'GET'), 404, {'detail': 'Friend request not found.'})

    def test_013_accept_own_send_friend_request(self):
        user1 = new_user()
        user2 = new_user()

        friend_request_id = self.assertResponse(friend_requests(user1, user2), 201, get_id=True)
        self.assertResponse(friend_request(friend_request_id, user1), 403, {'detail': 'you cannot accept your own friend request.'})


if __name__ == '__main__':
    unittest.main()
