from services.blocked import blocked_user, unblocked_user
from services.chat import accept_chat, create_chat, create_message, request_chat_id
from services.friend import create_friendship, friend_requests
from utils.credentials import new_user, guest_user
from utils.generate_random import rnstr
from utils.my_unittest import UnitTest


# todo test chat user endpoint
# todo test get chat of user blocked (do not see the chat)
class Test01_CreateChat(UnitTest):

    def test_001_accept_chat_from_anyone(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(accept_chat(user2), 200)
        self.assertResponse(create_chat(user1, user2['username']), 201)

    def test_002_accept_chat_from_friend_only(self):
        user1 = new_user()
        user2 = new_user()

        self.assertFriendResponse(create_friendship(user1, user2))
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

    def test_005_blocked_by_user(self):
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
        self.assertFriendResponse(create_friendship(user1, user2))
        self.assertResponse(create_chat(user1, user2['username']), 403, {'detail': 'This user does not accept new chat.'})

    def test_008_already_chat_with(self):
        user1 = new_user()
        user2 = new_user()

        self.assertFriendResponse(create_friendship(user1, user2))
        self.assertResponse(create_chat(user1, user2['username']), 201)
        self.assertResponse(create_chat(user1, user2['username']), 409, {'detail': 'You are already chat with this user.'})

    def test_009_blocked_user_trying_request(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(blocked_user(user1, user2['username']), 201)
        self.assertResponse(friend_requests(user1, user2), 403, {'detail': 'You blocked this user.'})

    def test_010_chat_with_guest(self):
        self.assertResponse(create_chat(new_user(), guest_user()['username']), 404, {'detail': 'User not found.'})


# todo add local possiblitie user
class Test03_GetChat(UnitTest):

    def test_001_get_chats(self):
        user1 = new_user()

        self.assertResponse(create_chat(user1, method='GET'), 200, count=0)

        for i in range(5):
            tmp_user = new_user()
            self.assertResponse(accept_chat(tmp_user), 200)
            self.assertResponse(create_chat(user1, tmp_user['username']), 201)

        self.assertResponse(create_chat(user1, method='GET'), 200, count=5)

    def test_002_search_chats(self):
        user1 = new_user()

        for i in range(5):
            tmp_user = new_user()
            self.assertResponse(accept_chat(tmp_user), 200)
            self.assertResponse(create_chat(user1, tmp_user['username']), 201)

        tmp_user = new_user('caca' + rnstr())
        self.assertResponse(accept_chat(tmp_user), 200)
        self.assertResponse(create_chat(user1, tmp_user['username']), 201)

        self.assertResponse(create_chat(user1, method='GET', data={'q': 'caca'}), 200, count=1)

        self.assertResponse(create_chat(user1, method='GET', data={'q': 'chat'}), 200, count=5)

    def test_003_search_chats_none(self):
        self.assertResponse(create_chat(new_user(), method='GET', data={'q': 'chat'}), 200, count=0)

    def test_004_blocked_chat(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(accept_chat(user2), 200)
        response = create_chat(user1, user2['username'])
        self.assertResponse(response, 201)
        chat_id = response.json['id']

        self.assertResponse(blocked_user(user1, user2['username']), 201)

        self.assertResponse(request_chat_id(user1, chat_id), 403, {'detail': 'You do not belong to this chat.'})
        self.assertResponse(request_chat_id(user2, chat_id), 403, {'detail': 'You do not belong to this chat.'})

    def test_005_get_chat_not_belong(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(accept_chat(user2), 200)
        response = create_chat(user1, user2['username'])
        self.assertResponse(response, 201)
        chat_id = response.json['id']

        self.assertResponse(request_chat_id(new_user(), chat_id), 403, {'detail': 'You do not belong to this chat.'})

    def test_006_do_not_view_chat(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(accept_chat(user2), 200)
        response = create_chat(user1, user2['username'])
        self.assertResponse(response, 201)
        chat_id = response.json['id']

        response = request_chat_id(user1, chat_id, {'view_chat': False}, 'PATCH')
        self.assertResponse(response, 200)
        for k in response.json['participants']:
            if k['id'] == user1['id']:
                self.assertFalse(k['view_chat'])
                break

        self.assertResponse(create_chat(user1, method='GET'), 200, count=0)

        self.assertResponse(create_chat(user2, method='GET'), 200, count=1)

        self.assertResponse(request_chat_id(user1, chat_id), 200)
        self.assertResponse(create_chat(user1, method='GET'), 200, count=1)

    def test_007_delete_chat(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(accept_chat(user2), 200)
        response = create_chat(user1, user2['username'])
        self.assertResponse(response, 201)
        chat_id = response.json['id']

        self.assertResponse(request_chat_id(user1, chat_id, method='DELETE'), 405, {'detail': 'Method "DELETE" not allowed.'})


class Test04_Messages(UnitTest):

    def send_message(self, user1=None, user2=None):
        if user1 is None:
            user1 = new_user()
        if user2 is None:
            user2 = new_user()

        self.assertResponse(accept_chat(user2), 200)

        response = create_chat(user1, user2['username'])
        self.assertResponse(response, 201)
        chat_id = response.json['id']
        self.assertResponse(create_message(user1, chat_id, 'Hey'), 201)
        self.assertResponse(create_message(user2, chat_id, 'Hi'), 201)
        self.assertResponse(create_message(user1, chat_id, 'How are you ?'), 201)
        self.assertResponse(create_message(user2, chat_id, 'goood !'), 201)
        self.assertResponse(create_message(user2, chat_id, 'and u ?'), 201)

        return chat_id

    def test_001_send_messages(self):
        user1 = new_user()

        chat_id = self.send_message(user1)
        response = request_chat_id(user1, chat_id)
        self.assertResponse(response, 200)
        self.assertEqual('and u ?', response.json['last_message']['content'])

    def test_002_get_messages(self):
        user1 = new_user()

        chat_id = self.send_message(user1)

        self.assertResponse(create_message(user1, chat_id, method='GET'), 200, count=5)

    def test_003_send_chat_does_not_exist(self):
        self.assertResponse(create_message(new_user(), '123456', 'test'), 403, {'detail': 'You do not belong to this chat.'})

    def test_004_send_chat_does_not_belong(self):
        user1 = new_user()

        self.assertResponse(accept_chat(user1), 200)

        response = create_chat(new_user(), user1['username'])
        self.assertResponse(response, 201)
        chat_id = response.json['id']

        self.assertResponse(create_message(new_user(), chat_id, 'test'), 403, {'detail': 'You do not belong to this chat.'})

    def test_005_chat_blocked(self):
        user1 = new_user()
        user2 = new_user()

        chat_id = self.send_message(user1, user2)

        response = blocked_user(user1, user2['username'])
        self.assertResponse(response, 201)
        block_id = response.json['id']

        self.assertResponse(request_chat_id(user1, chat_id), 403, {'detail': 'You do not belong to this chat.'})
        self.assertResponse(create_message(user1, chat_id, method='GET'), 403, {'detail': 'You do not belong to this chat.'})
        self.assertResponse(create_message(user1, chat_id, 'block'), 403, {'detail': 'You do not belong to this chat.'})

        self.assertResponse(unblocked_user(user1, block_id), 204)
        self.assertResponse(create_message(user1, chat_id, 'thank for unblocking me ;))'), 201)
        self.assertResponse(request_chat_id(user1, chat_id), 200)

    def test_006_do_not_view_chat(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(accept_chat(user2), 200)
        response = create_chat(user1, user2['username'])
        self.assertResponse(response, 201)
        chat_id = response.json['id']

        response = request_chat_id(user1, chat_id, {'view_chat': False}, 'PATCH')
        self.assertResponse(response, 200)
        for k in response.json['participants']:
            if k['id'] == user1['id']:
                self.assertFalse(k['view_chat'])
                break

        self.assertResponse(create_message(user1, chat_id, 'do not view chat'), 403, {'detail': 'You do not belong to this chat.'})

        self.assertResponse(create_chat(user1, method='GET'), 200, count=0)

        self.assertResponse(create_message(user2, chat_id, 'Hey how are you ?'), 201)

        self.assertResponse(create_chat(user1, method='GET'), 200, count=1)
        self.assertResponse(create_message(user1, chat_id, 'Fine and u?'), 201)


if __name__ == '__main__':
    unittest.main()
