from services.block import blocked_user
from services.chat import accept_chat, create_chat
from services.friend import create_friend, send_friend_request
from utils.credentials import new_user, guest_user
from utils.generate_random import rnstr
from utils.my_unittest import UnitTest


class Test01_CreateChat(UnitTest):

    def test_001_accept_chat_from_anyone(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(accept_chat(user2), 200)
        self.assertResponse(create_chat(user1, user2['username']), 201)

    def test_002_accept_chat_from_friend_only(self):
        user1 = new_user()
        user2 = new_user()

        self.assertFriendResponse(create_friend(user1, user2))
        self.assertResponse(create_chat(user1, user2['username']), 201)


class Test02_CreateChatError(UnitTest):

    def test_001_user_does_not_exist(self):
        self.assertResponse(create_chat(new_user(), 'caca_pipi_proute'), 404, {'detail': 'User not found.'})

    def test_002_invalid_type(self):
        user2 = new_user()

        self.assertResponse(accept_chat(user2), 200)
        self.assertResponse(create_chat(new_user(), data={'username': user2['username'], 'type': 'caca'}), 400, {'type': ["Chat type must be 'private_message', 'lobby', 'tournament' or 'custom_game'."]})

    def test_003_type_not_allowed(self):
        user2 = new_user()

        self.assertResponse(accept_chat(user2), 200)
        self.assertResponse(create_chat(new_user(), data={'username': user2['username'], 'type': 'tournament'}), 403, {'detail': 'You can only create private messages.'})

    def test_004_does_not_accept_chat(self):
        self.assertResponse(create_chat(new_user(), new_user()['username']), 403, {'detail': 'This user does not accept new chat.'})

    def test_005_blok_by_user(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(blocked_user(user1, user2['username']), 201)
        self.assertResponse(create_chat(user2, user1['username']), 404, {'detail': 'User not found.'})

    def test_006_chat_with_myself(self):
        user1 = new_user()

        self.assertResponse(create_chat(user1, user1['username']), 403, {'detail': 'You cannot chat with yourself.'})

    def test_007_accept_chat_from_none(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(accept_chat(user2, 'none'), 200)
        self.assertFriendResponse(create_friend(user1, user2))
        self.assertResponse(create_chat(user1, user2['username']), 403, {'detail': 'This user does not accept new chat.'})

    def test_008_already_chat_with(self):
        user1 = new_user()
        user2 = new_user()

        self.assertFriendResponse(create_friend(user1, user2))
        self.assertResponse(create_chat(user1, user2['username']), 201)
        self.assertResponse(create_chat(user1, user2['username']), 409, {'detail': 'You are already chat with this user.'})

    def test_009_blok_user_trying_request(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(blocked_user(user1, user2['username']), 201)
        self.assertResponse(send_friend_request(user1, user2), 403, {'detail': 'You blocked this user.'})

    def test_010_chat_with_guest(self):
        self.assertResponse(create_chat(new_user(), guest_user()['username']), 404, {'detail': 'User not found.'})


class Test03_GetChat(UnitTest):

    def test_001_get_chats(self):
        user1 = new_user()

        response = create_chat(user1, method='GET')
        self.assertResponse(response, 200)
        self.assertEqual(0, len(response.json['results']))

        for i in range(5):
            tmp_user = new_user()
            self.assertResponse(accept_chat(tmp_user), 200)
            self.assertResponse(create_chat(user1, tmp_user['username']), 201)

        response = create_chat(user1, method='GET')
        self.assertResponse(response, 200)
        self.assertEqual(5, len(response.json['results']))

    def test_002_search_chats(self):
        user1 = new_user()

        for i in range(5):
            tmp_user = new_user()
            self.assertResponse(accept_chat(tmp_user), 200)
            self.assertResponse(create_chat(user1, tmp_user['username']), 201)

        tmp_user = new_user('caca' + rnstr())
        self.assertResponse(accept_chat(tmp_user), 200)
        self.assertResponse(create_chat(user1, tmp_user['username']), 201)

        response = create_chat(user1, method='GET', data={'q': 'caca'})
        self.assertResponse(response, 200)
        self.assertEqual(1, len(response.json['results']))

        response = create_chat(user1, method='GET', data={'q': 'chat'})
        self.assertResponse(response, 200)
        self.assertEqual(5, len(response.json['results']))

    def test_003_search_chats_none(self):
        response = create_chat(new_user(), method='GET', data={'q': 'chat'})
        self.assertResponse(response, 200)
        self.assertEqual(0, len(response.json['results']))

    def test_004_blocked_chats(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(accept_chat(user2), 200)
        self.assertResponse(create_chat(user1, user2['username']), 201)
        self.assertResponse(blocked_user(user1, user2['username']), 201)

        response = create_chat(new_user(), method='GET')
        self.assertResponse(response, 200)
        self.assertEqual(0, len(response.json['results']))


if __name__ == '__main__':
    unittest.main()
