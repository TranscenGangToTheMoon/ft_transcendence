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


if __name__ == '__main__':
    unittest.main()
