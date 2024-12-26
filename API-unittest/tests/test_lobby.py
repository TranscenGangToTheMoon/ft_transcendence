import unittest

from services.blocked import blocked_user, unblocked_user
from services.lobby import create_lobby, join_lobby, kick_user
from utils.my_unittest import UnitTest


class Test01_JoinLobby(UnitTest):

    def test_001_create_lobby(self):
        user1 = self.user_sse()

        self.assertResponse(create_lobby(user1), 201)
        user1['thread'].join()

    def test_002_join_lobby(self):
        user1 = self.user_sse(['lobby-join'])
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(join_lobby(user2, code), 201)
        user1['thread'].join()
        user2['thread'].join()


class Test02_ErrorJoinLobby(UnitTest):

    def test_001_lobby_does_not_exist(self):
        user1 = self.user_sse()

        self.assertResponse(join_lobby(user1, '123456'), 404, {'detail': 'Lobby not found.'})
        user1['thread'].join()

    def test_002_already_join(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(join_lobby(user2, code), 201)
        self.assertResponse(join_lobby(user1, code), 409, {'detail': 'You already joined this lobby.'})
        self.assertResponse(join_lobby(user2, code), 409, {'detail': 'You already joined this lobby.'})
        user1['thread'].join()
        user2['thread'].join()

    def test_003_lobby_is_full(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')
        for _ in range(2):
            user_tmp = self.user_sse()
            self.assertResponse(join_lobby(user_tmp, code), 201)

        self.assertResponse(join_lobby(user2, code), 403, {'detail': 'Lobby is full.'})
        user1['thread'].join()
        user2['thread'].join()

    def test_004_guest_create_lobby(self):
        user1 = self.guest_user(connect_sse=True)

        self.assertResponse(create_lobby(user1), 403, {'detail': 'Guest users cannot create lobby.'})

    def test_005_invalid_game_mode(self):
        user1 = self.user_sse()

        self.assertResponse(create_lobby(user1, data={'game_mode': 'sdfsdf'}), 400, {'game_mode': ["Game mode must be 'clash' or 'custom_game'."]})
        user1['thread'].join()

    def test_006_no_game_mode(self):
        user1 = self.user_sse()

        self.assertResponse(create_lobby(user1, data={}), 400, {'game_mode': ['This field is required.']})
        user1['thread'].join()

    def test_007_blocked_user_cannot_join(self):
        user1 = self.user_sse()
        user2 = self.user_sse(get_me=True)

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(blocked_user(user1, user2['id']), 201)
        self.assertResponse(join_lobby(user2, code), 404, {'detail': 'Lobby not found.'})
        user1['thread'].join()
        user2['thread'].join()

    def test_008_blocked_user_kick_user(self):
        user1 = self.user_sse()
        user2 = self.user_sse(get_me=True)

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(join_lobby(user2, code), 201)
        self.assertResponse(blocked_user(user1, user2['id']), 201)

        response = self.assertResponse(join_lobby(user1, code, 'GET'), 200)
        self.assertEqual(1, len(response))

        self.assertResponse(create_lobby(user2, method='GET'), 404, {'detail': 'You do not belong to any lobby.'})
        self.assertResponse(join_lobby(user2, code), 404, {'detail': 'Lobby not found.'})
        user1['thread'].join()
        user2['thread'].join()

    def test_009_blocked_user_not_creator(self):
        user1 = self.user_sse()
        user2 = self.user_sse()
        user3 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(join_lobby(user2, code), 201)
        self.assertResponse(join_lobby(user3, code), 201)
        self.assertResponse(blocked_user(user2, user3['id']), 201)

        response = self.assertResponse(join_lobby(user1, code, 'GET'), 200)
        self.assertEqual(3, len(response))
        user1['thread'].join()
        user2['thread'].join()
        user3['thread'].join()

    def test_010_blocked_then_unblock(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(join_lobby(user2, code), 201)
        blocked_id = self.assertResponse(blocked_user(user1, user2['id']), 201, get_field=True)

        response = self.assertResponse(join_lobby(user1, code, 'GET'), 200)
        self.assertEqual(1, len(response))

        self.assertResponse(join_lobby(user2, code), 404, {'detail': 'Lobby not found.'})
        self.assertResponse(unblocked_user(user1, blocked_id), 204)
        self.assertResponse(join_lobby(user2, code), 201)
        user1['thread'].join()
        user2['thread'].join()

    def test_011_join_lobby_without_sse(self):
        user1 = self.new_user()
        user2 = self.user_sse()

        self.assertResponse(create_lobby(user1), 401, {'detail': 'You need to be connected to SSE to access this resource'})
        code = self.assertResponse(create_lobby(user2), 201, get_field='code')
        self.assertResponse(join_lobby(user1, code), 401, {'detail': 'You need to be connected to SSE to access this resource'})
        user2['thread'].join()


class Test03_KickLobby(UnitTest):

    def test_001_kick_lobby(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(join_lobby(user2, code), 201)
        self.assertResponse(kick_user(user1, user2, code), 204)

        response = self.assertResponse(join_lobby(user1, code, 'GET'), 200)
        self.assertEqual(1, len(response))
        user1['thread'].join()
        user2['thread'].join()

    def test_002_user_kick_not_join_lobby(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(kick_user(user2, user1, code), 403, {'detail': 'You do not belong to this lobby.'})
        user1['thread'].join()
        user2['thread'].join()

    def test_003_user_kicked_not_join_lobby(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(kick_user(user1, user2, code), 404, {'detail': 'This user does not belong to this lobby.'})
        user1['thread'].join()
        user2['thread'].join()

    def test_004_invalid_lobby(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        self.assertResponse(kick_user(user1, user2, '123456'), 403, {'detail': 'You do not belong to this lobby.'})
        user1['thread'].join()
        user2['thread'].join()

    def test_005_not_creator(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(join_lobby(user2, code), 201)
        self.assertResponse(kick_user(user2, user1, code), 403, {'detail': 'Only creator can update this lobby.'})
        user1['thread'].join()
        user2['thread'].join()

    def test_006_users_does_exist(self):
        user1 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')
        self.assertResponse(kick_user(user1, {'id': 123456789}, code), 404, {'detail': 'This user does not belong to this lobby.'})
        user1['thread'].join()


class Test04_UpdateLobby(UnitTest):

    def test_001_update_lobby(self):
        user1 = self.user_sse()

        self.assertResponse(create_lobby(user1, data={'game_mode': 'custom_game'}), 201, get_field='code')
        self.assertEqual('3v3', self.assertResponse(create_lobby(user1, {'match_type': '3v3'}, 'PATCH'), 200, get_field='match_type'))
        user1['thread'].join()

    def test_002_invalid_match_type(self):
        user1 = self.user_sse()

        self.assertResponse(create_lobby(user1, data={'game_mode': 'custom_game'}), 201)
        self.assertResponse(create_lobby(user1, data={'match_type': 42}, method='PATCH'), 400, {'match_type': ["Match type must be '1v1' or '3v3'."]})
        self.assertResponse(create_lobby(user1, data={'match_type': 'cac'}, method='PATCH'), 400, {'match_type': ["Match type must be '1v1' or '3v3'."]})
        user1['thread'].join()

    def test_003_update_not_creator(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1, data={'game_mode': 'custom_game'}), 201, get_field='code')

        self.assertResponse(join_lobby(user2, code), 201)
        self.assertResponse(create_lobby(user2, data={'match_type': '3v3'}, method='PATCH'), 403, {'detail': 'Only creator can update this lobby.'})
        user1['thread'].join()
        user2['thread'].join()

    def test_004_update_clash(self):
        user1 = self.user_sse()

        self.assertResponse(create_lobby(user1), 201)
        self.assertResponse(create_lobby(user1, data={'match_type': '3v3'}, method='PATCH'), 403, {'detail': 'You cannot update clash lobby.'})
        user1['thread'].join()

    def test_005_update_game_mode(self):
        user1 = self.user_sse()

        self.assertResponse(create_lobby(user1, data={'game_mode': 'custom_game'}), 201)
        self.assertResponse(create_lobby(user1, data={'game_mode': 'clash'}, method='PATCH'), 403, {'detail': 'You cannot update game mode.'})
        user1['thread'].join()

    def test_006_update_match_type_when_full(self):
        user1 = self.user_sse()
        users = [self.user_sse() for _ in range(5)]

        code = self.assertResponse(create_lobby(user1, data={'game_mode': 'custom_game'}), 201, get_field='code')

        response = self.assertResponse(create_lobby(user1, data={'match_type': '3v3'}, method='PATCH'), 200)
        self.assertEqual('3v3', response['match_type'])

        teams = ['Team A', 'Team A', 'Team B', 'Team B', 'Team B']
        for i in range(5):
            response = self.assertResponse(join_lobby(users[i], code), 201)
            for user in response['participants']:
                if user['id'] == users[i]['id']:
                    self.assertEqual(teams[i], user['team'])
                    break

        response = self.assertResponse(create_lobby(user1, data={'match_type': '1v1'}, method='PATCH'), 200)
        self.assertEqual('1v1', response['match_type'])

        teams = ['Spectator', 'Spectator', 'Team B', 'Spectator', 'Spectator']
        for i in range(5):
            response = self.assertResponse(join_lobby(users[i], code, method='GET'), 200)
            for user in response:
                if user['id'] == users[i]['id']:
                    self.assertEqual(teams[i], user['team'])
                    break
        user1['thread'].join()
        [u['thread'].join() for u in users]


class Test05_UpdateParticipantLobby(UnitTest):

    def test_001_set_ready_to_true(self):
        user1 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        response = self.assertResponse(join_lobby(user1, code, data={'is_ready': True}), 200)
        self.assertTrue(response['is_ready'])
        user1['thread'].join()

    def test_002_change_team(self):
        user1 = self.user_sse()

        code = self.assertResponse(create_lobby(user1, data={'game_mode': 'custom_game'}), 201, get_field='code')

        response = self.assertResponse(join_lobby(user1, code, data={'team': 'Team B'}), 200)
        self.assertEqual('Team B', response['team'])

        response = self.assertResponse(join_lobby(user1, code, data={'team': 'Spectator'}), 200)
        self.assertEqual('Spectator', response['team'])
        user1['thread'].join()

    def test_003_change_invalid_team(self):
        user1 = self.user_sse()

        code = self.assertResponse(create_lobby(user1, data={'game_mode': 'custom_game'}), 201, get_field='code')
        self.assertResponse(join_lobby(user1, code, data={'team': 'Team caca'}), 400, {'team': ["Match type must be 'Team A', 'Team B' or 'Spectator'."]})
        user1['thread'].join()

    def test_004_change_team_already_in(self):
        user1 = self.user_sse()

        code = self.assertResponse(create_lobby(user1, data={'game_mode': 'custom_game'}), 201, get_field='code')
        self.assertResponse(join_lobby(user1, code, data={'team': 'Team A'}), 409, {'detail': 'You are already in this team.'})
        user1['thread'].join()

    def test_005_change_team_full(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1, data={'game_mode': 'custom_game'}), 201, get_field='code')

        self.assertResponse(join_lobby(user2, code), 201)
        self.assertResponse(join_lobby(user2, code, method='PATCH', data={'team': 'Team A'}), 403, {'detail': 'Team is full.'})
        user1['thread'].join()


class Test06_LeaveLobby(UnitTest):

    def test_001_leave_lobby(self):
        user1 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(join_lobby(user1, code, 'DELETE'), 204)
        self.assertResponse(join_lobby(user1, code, 'GET'), 403, {'detail': 'You do not belong to this lobby.'})
        self.assertResponse(create_lobby(user1, method='GET'), 404, {'detail': 'You do not belong to any lobby.'})
        user1['thread'].join()

    def test_002_leave_lobby_then_other_member_became_creator(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(join_lobby(user2, code), 201)
        self.assertResponse(join_lobby(user1, code, 'DELETE'), 204)

        response = self.assertResponse(join_lobby(user2, code, 'GET'), 200)
        self.assertEqual(1, len(response))
        self.assertTrue(response[0]['creator'])
        user1['thread'].join()
        user2['thread'].join()

    def test_003_guest_join_leave_lobby_then_destroy_lobby(self):
        user1 = self.user_sse()
        user2 = self.guest_user()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(join_lobby(user2, code), 201)
        self.assertResponse(join_lobby(user1, code, 'DELETE'), 204)
        self.assertResponse(join_lobby(user2, code, 'GET'), 403, {'detail': 'You do not belong to this lobby.'})
        self.assertResponse(create_lobby(user2, method='GET'), 404, {'detail': 'You do not belong to any lobby.'})
        user1['thread'].join()
        user2['thread'].join()

    def test_004_leave_lobby_does_not_exist(self):
        user1 = self.user_sse()

        self.assertResponse(join_lobby(user1, '123456', method='DELETE'), 403, {'detail': 'You do not belong to this lobby.'})
        user1['thread'].join()

    def test_005_leave_lobby_does_not_join(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')
        self.assertResponse(join_lobby(user2, code, 'DELETE'), 403, {'detail': 'You do not belong to this lobby.'})
        user1['thread'].join()
        user2['thread'].join()

    def test_006_leave_lobby_not_creator(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(join_lobby(user2, code), 201)
        self.assertResponse(join_lobby(user2, code, 'DELETE'), 204)

        response = self.assertResponse(join_lobby(user1, code, 'GET'), 200)
        self.assertEqual(1, len(response))
        user1['thread'].join()
        user2['thread'].join()


class Test07_GetLobby(UnitTest):

    def test_001_get_lobby(self):
        user1 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        response = self.assertResponse(create_lobby(user1, method='GET'), 200)
        self.assertEqual(code, response['code'])
        user1['thread'].join()

    def test_002_get_lobby_does_not_join(self):
        user1 = self.user_sse()

        self.assertResponse(create_lobby(user1, method='GET'), 404, {'detail': 'You do not belong to any lobby.'})
        user1['thread'].join()

    def test_002_get_lobby_participant(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(join_lobby(user2, code), 201)

        response = self.assertResponse(join_lobby(user1, code, 'GET'), 200)
        self.assertEqual(2, len(response))
        user1['thread'].join()
        user2['thread'].join()

    def test_003_get_lobby_participant_does_not_join(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_lobby(user1), 201, get_field='code')

        self.assertResponse(join_lobby(user2, code, 'GET'), 403, {'detail': 'You do not belong to this lobby.'})
        user1['thread'].join()
        user2['thread'].join()


if __name__ == '__main__':
    unittest.main()
