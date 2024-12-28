import unittest

from services.blocked import blocked_user
from services.friend import create_friendship, friend_request, friend_requests, get_friend_requests_received, \
    get_friends, friend
from services.user import me
from utils.my_unittest import UnitTest


class Test01_Friend(UnitTest):

    def test_001_friend(self):
        user1 = self.user_sse(['accept-friend-request'])
        user2 = self.user_sse(['receive-friend-request'])

        self.assertFriendResponse(create_friendship(user1, user2))
        user1['thread'].join()
        user2['thread'].join()

    def test_002_friend_without_friend_request(self):
        user1 = self.new_user()

        self.assertResponse(friend_request('123456', user1), 404, {'detail': 'Friend request not found.'})

    def test_003_get_friends(self):
        user1 = self.new_user()

        for i in range(7):
            user_tmp = self.new_user()

            self.assertFriendResponse(create_friendship(user1, user_tmp))

        self.assertResponse(get_friends(user1), 200, count=7)

    def test_004_friends_then_block(self):
        user1 = self.new_user()
        user2 = self.new_user(get_me=True)

        self.assertFriendResponse(create_friendship(user1, user2))
        self.assertResponse(get_friends(user2), 200, count=1)

        self.assertResponse(blocked_user(user1, user2['id']), 201)

        for u in (user1, user2):
            self.assertResponse(get_friends(u), 200, count=0)

    def test_005_delete_friend_user1(self):
        user1 = self.new_user()
        user2 = self.new_user()

        friendship_id = self.assertFriendResponse(create_friendship(user1, user2))
        self.assertResponse(friend(user1, friendship_id), 200)
        self.assertResponse(friend(user1, friendship_id, 'DELETE'), 204)

        self.assertResponse(friend(user1, friendship_id), 404, {'detail': 'Friendship not found.'})
        self.assertResponse(get_friends(user2), 200, count=0)

    def test_006_delete_friend_user2(self):
        user1 = self.new_user()
        user2 = self.new_user()

        friendship_id = self.assertFriendResponse(create_friendship(user1, user2))
        self.assertResponse(friend(user1, friendship_id), 200)
        self.assertResponse(friend(user2, friendship_id, 'DELETE'), 204)

        self.assertResponse(friend(user2, friendship_id), 404, {'detail': 'Friendship not found.'})
        self.assertResponse(get_friends(user1), 200, count=0)

    def test_007_delete_friend_not_belong_user(self):
        user1 = self.new_user()
        user2 = self.new_user()
        user3 = self.new_user()

        friendship_id = self.assertFriendResponse(create_friendship(user1, user2))
        self.assertResponse(friend(user1, friendship_id), 200)

        self.assertResponse(friend(user3, friendship_id, 'DELETE'), 404, {'detail': 'Friendship not found.'})
        self.assertResponse(friend(user1, friendship_id), 200)

    def test_008_delete_friend_sse(self):
        user1 = self.user_sse(['accept-friend-request', 'delete-friend', 'accept-friend-request', 'delete-friend', 'accept-friend-request', 'delete-friend'], get_me=True)
        user2 = self.new_user()
        user3 = self.new_user()
        user4 = self.new_user()

        friendship_id = self.assertFriendResponse(create_friendship(user1, user2))
        self.assertResponse(friend(user2, friendship_id, 'DELETE'), 204)
        self.assertResponse(friend(user1, friendship_id), 404, {'detail': 'Friendship not found.'})

        friendship_id = self.assertFriendResponse(create_friendship(user1, user3))
        self.assertResponse(blocked_user(user3, user1['id']), 201)
        self.assertResponse(friend(user1, friendship_id), 404, {'detail': 'Friendship not found.'})

        friendship_id = self.assertFriendResponse(create_friendship(user1, user4))
        self.assertResponse(me(user4, 'DELETE', password=True), 204)
        self.assertResponse(friend(user1, friendship_id), 404, {'detail': 'Friendship not found.'})

        user1['thread'].join()


class Test02_FriendRequest(UnitTest):

    def test_001_friend_request(self):
        user1 = self.new_user()
        user2 = self.user_sse(['receiveaccept-friend-request'])

        friend_request_id = self.assertResponse(friend_requests(user1, user2), 201, get_field=True)

        self.assertResponse(get_friend_requests_received(user2), 200, count=1)
        self.assertResponse(friend_requests(user1, method='GET'), 200, count=1)
        self.assertResponse(friend_request(friend_request_id, user1, method='GET'), 200)
        self.assertResponse(friend_request(friend_request_id, user2, method='GET'), 200)
        user2['thread'].join()

    def test_002_user_does_not_exist(self):
        user1 = self.new_user()

        self.assertResponse(friend_requests(user1, {'username': 'caca'}), 404, {'detail': 'User not found.'})

    def test_003_already_request(self):
        user1 = self.new_user()
        user2 = self.new_user()

        self.assertResponse(friend_requests(user1, user2), 201)
        self.assertResponse(friend_requests(user1, user2), 409, {'detail': 'You have already sent a friend request to this user.'})
        self.assertResponse(friend_requests(user2, user1), 409, {'detail': 'You have already received a friend request from this user.'})

    def test_004_already_friends(self):
        user1 = self.new_user()
        user2 = self.new_user()

        self.assertFriendResponse(create_friendship(user1, user2))
        self.assertResponse(friend_requests(user1, user2), 409, {'detail': 'You are already friends with this user.'})

    def test_005_send_friend_request_then_blocked(self):
        user1 = self.new_user(get_me=True)
        user2 = self.new_user()

        self.assertResponse(friend_requests(user1, user2), 201)
        self.assertResponse(blocked_user(user2, user1['id']), 201)
        self.assertResponse(get_friend_requests_received(user2), 200, count=0)
        self.assertResponse(friend_requests(user1, method='GET'), 200, count=0)

    def test_006_blocked_then_send_friend_request(self):
        user1 = self.new_user()
        user2 = self.new_user(get_me=True)

        self.assertResponse(blocked_user(user1, user2['id']), 201)
        self.assertResponse(friend_requests(user1, user2), 403, {'detail': 'You blocked this user.'})
        self.assertResponse(friend_requests(user2, user1), 404, {'detail': 'User not found.'})

    def test_007_send_friend_request_to_myself(self):
        user1 = self.new_user()

        self.assertResponse(friend_requests(user1, user1), 403, {'detail': 'You cannot send a friend request to yourself.'})

    def test_008_forget_username_field(self):
        user1 = self.new_user()

        self.assertResponse(friend_requests(user1, data={}), 400, {'username': ['This field is required.']})

    def test_009_get_friend_request_not_belong(self):
        user1 = self.new_user()
        user2 = self.new_user()
        user3 = self.new_user()

        friend_request_id = self.assertResponse(friend_requests(user1, user2), 201, get_field=True)

        self.assertResponse(friend_request(friend_request_id, user3), 404, {'detail': 'Friend request not found.'})

    def test_010_reject_friend_request(self):
        user1 = self.user_sse(['reject-friend-request', 'reject-friend-request', 'reject-friend-request'], get_me=True)
        user2 = self.user_sse(['receive-friend-request'])
        user3 = self.user_sse(['receive-friend-request'])
        user4 = self.user_sse(['receive-friend-request'])

        friend_request_id = self.assertResponse(friend_requests(user1, user2), 201, get_field=True)
        self.assertResponse(friend_request(friend_request_id, user2, 'DELETE'), 204)
        self.assertResponse(friend_request(friend_request_id, user1, 'GET'), 404, {'detail': 'Friend request not found.'})

        friend_request_id = self.assertResponse(friend_requests(user1, user3), 201, get_field=True)
        self.assertResponse(blocked_user(user3, user1['id']), 201)
        self.assertResponse(friend_request(friend_request_id, user1, 'GET'), 404, {'detail': 'Friend request not found.'})

        friend_request_id = self.assertResponse(friend_requests(user1, user4), 201, get_field=True)
        self.assertResponse(me(user4, 'DELETE', password=True), 204)
        self.assertResponse(friend_request(friend_request_id, user1, 'GET'), 404, {'detail': 'Friend request not found.'})

        user1['thread'].join()
        user2['thread'].join()
        user3['thread'].join()
        user4['thread'].join()

    def test_011_cancel_friend_request(self):
        user1 = self.user_sse(['receive-friend-request', 'cancel-friend-request', 'receive-friend-request', 'cancel-friend-request', 'receive-friend-request', 'cancel-friend-request'], get_me=True)
        user2 = self.new_user()
        user3 = self.new_user()
        user4 = self.new_user()

        friend_request_id = self.assertResponse(friend_requests(user2, user1), 201, get_field=True)
        self.assertResponse(friend_request(friend_request_id, user2, 'DELETE'), 204)
        self.assertResponse(friend_request(friend_request_id, user1, 'GET'), 404, {'detail': 'Friend request not found.'})
        self.assertResponse(friend_request(friend_request_id, user2, 'GET'), 404, {'detail': 'Friend request not found.'})

        friend_request_id = self.assertResponse(friend_requests(user3, user1), 201, get_field=True)
        self.assertResponse(blocked_user(user3, user1['id']), 201)
        self.assertResponse(friend_request(friend_request_id, user1, 'GET'), 404, {'detail': 'Friend request not found.'})
        self.assertResponse(friend_request(friend_request_id, user2, 'GET'), 404, {'detail': 'Friend request not found.'})

        friend_request_id = self.assertResponse(friend_requests(user4, user1), 201, get_field=True)
        self.assertResponse(me(user4, 'DELETE', password=True), 204)
        self.assertResponse(friend_request(friend_request_id, user1, 'GET'), 404, {'detail': 'Friend request not found.'})

        user1['thread'].join()

    def test_012_delete_friend_request_after_became_friend(self):
        user1 = self.new_user()
        user2 = self.new_user()

        friend_request_id = self.assertResponse(friend_requests(user1, user2), 201, get_field=True)
        self.assertResponse(friend_request(friend_request_id, user2), 201, get_field=True)
        self.assertResponse(friend_request(friend_request_id, user1, 'GET'), 404, {'detail': 'Friend request not found.'})
        self.assertResponse(friend_request(friend_request_id, user2, 'GET'), 404, {'detail': 'Friend request not found.'})

    def test_013_accept_own_send_friend_request(self):
        user1 = self.new_user()
        user2 = self.new_user()

        friend_request_id = self.assertResponse(friend_requests(user1, user2), 201, get_field=True)
        self.assertResponse(friend_request(friend_request_id, user1), 403, {'detail': 'you cannot accept your own friend request.'})

    def test_014_guest_user_make_friend_request(self):
        user1 = self.guest_user()
        user2 = self.new_user()

        self.assertResponse(friend_requests(user1, user2), 403, {'detail': 'Guest users cannot make friend request.'})

    def test_015_guest_user_receive_friend_request(self):
        user1 = self.new_user()
        user2 = self.guest_user(get_me=True)

        self.assertResponse(friend_requests(user1, user2), 404, {'detail': 'User not found.'})

    def test_016_friend_request_receive(self):
        user1 = self.new_user()
        user2 = self.new_user()
        n = 4

        self.assertEqual(0, self.assertResponse(me(user1), 200, get_field='notifications')['friend_requests'])

        friend_request_id = self.assertResponse(friend_requests(user2, user1), 201, get_field=True)
        for _ in range(n):
            user_tmp = self.new_user()
            self.assertResponse(friend_requests(user_tmp, receiver=user1), 201)

        self.assertResponse(get_friend_requests_received(user2), 200)
        self.assertEqual(n + 1, self.assertResponse(me(user1), 200, get_field='notifications')['friend_requests'])
        self.assertResponse(friend_request(friend_request_id, user2, 'DELETE'), 204)
        self.assertEqual(n, self.assertResponse(me(user1), 200, get_field='notifications')['friend_requests'])
        self.assertResponse(get_friend_requests_received(user1), 200)
        self.assertEqual(0, self.assertResponse(me(user1), 200, get_field='notifications')['friend_requests'])

    def test_017_new_field(self):
        user1 = self.new_user()
        user2 = self.new_user()

        self.assertResponse(friend_requests(user2, user1), 201)
        response = self.assertResponse(get_friend_requests_received(user1), 200, get_field='results')
        self.assertIn('new', response[0])
        self.assertEqual(response[0]['new'], True)
        response = self.assertResponse(friend_requests(user2, method='GET'), 200, get_field='results')
        self.assertNotIn('new', response[0])

    def test_018_no_friend_request(self):
        user1 = self.new_user()

        self.assertEqual(0, self.assertResponse(me(user1), 200, get_field='notifications')['friend_requests'])


if __name__ == '__main__':
    unittest.main()
