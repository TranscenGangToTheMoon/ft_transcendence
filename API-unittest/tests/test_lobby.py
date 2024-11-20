from services.blocked import blocked_user
from services.lobby import create_lobby, join_lobby, kick_user
from utils.credentials import new_user, guest_user
from utils.my_unittest import UnitTest


class Test01_JoinLobby(UnitTest):

    def test_001_create_lobby(self):
        self.assertResponse(create_lobby(), 201)

    def test_002_join_lobby(self):
        response = create_lobby()
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code), 201)


class Test02_ErrorJoinLobby(UnitTest):

    def test_001_lobby_does_not_exist(self):
        self.assertResponse(join_lobby('123456'), 404, {'detail': 'Lobby not found.'})

    def test_002_already_join(self):
        user1 = new_user()
        user2 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user2), 201)
        self.assertResponse(join_lobby(code, user1), 409, {'detail': 'You already joined this lobby.'})
        self.assertResponse(join_lobby(code, user2), 409, {'detail': 'You already joined this lobby.'})

    def test_003_lobby_is_full(self):
        response = create_lobby()
        self.assertResponse(response, 201)

        code = response.json['code']
        for _ in range(2):
            self.assertResponse(join_lobby(code), 201)
        self.assertResponse(join_lobby(code), 403, {'detail': 'Lobby is full.'})

    def test_004_guest_create_lobby(self):
        self.assertResponse(create_lobby(guest_user()), 403, {'detail': 'Guest users cannot create lobby.'})

    def test_005_invalid_game_mode(self):
        self.assertResponse(create_lobby(data={'game_mode': 'sdfsdf'}), 400, {'game_mode': ["Game mode must be 'clash' or 'custom_game'."]})

    def test_006_no_game_mode(self):
        self.assertResponse(create_lobby(data={}), 400, {'game_mode': ['This field is required.']})

    def test_007_blocked_user_cannot_join(self):
        user1 = new_user()
        user2 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(blocked_user(user1, user2['username']), 201)
        self.assertResponse(join_lobby(code, user2), 404, {'detail': 'Lobby not found.'})

    def test_008_blocked_user_kick_user(self):
        user1 = new_user()
        user2 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user2), 201)
        self.assertResponse(blocked_user(user1, user2['username']), 201)

        response = join_lobby(code, user1, 'GET')
        self.assertResponse(response, 200)
        self.assertEqual(1, len(response.json))

        self.assertResponse(create_lobby(user2, method='GET'), 404, {'detail': 'You do not belong to any lobby.'})

    def test_009_blocked_user_not_creator(self):
        user1 = new_user()
        user2 = new_user()
        user3 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user2), 201)
        self.assertResponse(join_lobby(code, user3), 201)
        self.assertResponse(blocked_user(user2, user3['username']), 201)

        response = join_lobby(code, user1, 'GET')
        self.assertResponse(response, 200)
        self.assertEqual(3, len(response.json))


class Test03_KickLobby(UnitTest):

    def test_001_kick_lobby(self):
        user1 = new_user()
        user2 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user2), 201)
        self.assertResponse(kick_user(user1, user2, code), 204)

        response = join_lobby(code, user1, 'GET')
        self.assertResponse(response, 200)
        self.assertEqual(1, len(response.json))

    def test_002_user_kick_not_join_lobby(self):
        user1 = new_user()
        user2 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(kick_user(user2, user1, code), 403, {'detail': 'You do not belong to this lobby.'})

    def test_003_user_kicked_not_join_lobby(self):
        user1 = new_user()
        user2 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(kick_user(user1, user2, code), 404, {'detail': 'This user does not belong to this lobby.'})

    def test_004_invalid_lobby(self):
        self.assertResponse(kick_user(new_user(), new_user(), '123456'), 403, {'detail': 'You do not belong to this lobby.'})

    def test_005_not_creator(self):
        user1 = new_user()
        user2 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user2), 201)
        self.assertResponse(kick_user(user2, user1, code), 403, {'detail': 'Only creator can update this lobby.'})

    def test_006_users_does_exist(self):
        user1 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(kick_user(user1, {'id': 123456789}, code), 404, {'detail': 'This user does not belong to this lobby.'})


class Test04_UpdateLobby(UnitTest):

    def test_001_update_lobby(self):
        user1 = new_user()

        response = create_lobby(user1, data={'game_mode': 'custom_game'})
        self.assertResponse(response, 201)
        code = response.json['code']

        response = create_lobby(user1, {'bo': 1, 'match_type': '3v3'}, 'PATCH')
        self.assertResponse(response, 200)
        self.assertEqual(1, response.json['bo'])
        self.assertEqual('3v3', response.json['match_type'])

    def test_002_invalid_match_type(self):
        user1 = new_user()

        self.assertResponse(create_lobby(user1, data={'game_mode': 'custom_game'}), 201)
        self.assertResponse(create_lobby(user1, data={'match_type': 42}, method='PATCH'), 400, {'match_type': ["Match type must be '1v1' or '3v3'."]})
        self.assertResponse(create_lobby(user1, data={'match_type': 'cac'}, method='PATCH'), 400, {'match_type': ["Match type must be '1v1' or '3v3'."]})

    def test_003_invalid_bo(self):
        user1 = new_user()

        self.assertResponse(create_lobby(user1, data={'game_mode': 'custom_game'}), 201)
        self.assertResponse(create_lobby(user1, data={'bo': 42}, method='PATCH'), 400, {'bo': ['Best of must be 1, 3 or 5.']})
        self.assertResponse(create_lobby(user1, data={'bo': 'caca'}, method='PATCH'), 400, {'bo': ['A valid integer is required.']})

    def test_004_update_not_creator(self):
        user1 = new_user()
        user2 = new_user()

        response = create_lobby(user1, data={'game_mode': 'custom_game'})
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user2), 201)
        self.assertResponse(create_lobby(user2, data={'bo': 3}, method='PATCH'), 403, {'detail': 'Only creator can update this lobby.'})

    def test_005_update_clash(self):
        user1 = new_user()

        self.assertResponse(create_lobby(user1), 201)
        self.assertResponse(create_lobby(user1, data={'bo': 1}, method='PATCH'), 403, {'detail': 'You cannot update clash lobby.'})

    def test_006_update_game_mode(self):
        user1 = new_user()

        self.assertResponse(create_lobby(user1, data={'game_mode': 'custom_game'}), 201)
        self.assertResponse(create_lobby(user1, data={'game_mode': 'clash'}, method='PATCH'), 403, {'detail': 'You cannot update game mode.'})

    def test_007_update_match_type_when_full(self):
        user1 = new_user()
        users = [new_user() for _ in range(5)]

        response = create_lobby(user1, data={'game_mode': 'custom_game'})
        self.assertResponse(response, 201)
        code = response.json['code']

        response = create_lobby(user1, data={'match_type': '3v3'}, method='PATCH')
        self.assertResponse(response, 200)
        self.assertEqual('3v3', response.json['match_type'])

        teams = ['Team A', 'Team A', 'Team B', 'Team B', 'Team B']
        for i in range(5):
            response = join_lobby(code, users[i])
            self.assertResponse(response, 201)
            self.assertEqual(teams[i], response.json['team'])

        response = create_lobby(user1, data={'match_type': '1v1'}, method='PATCH')
        self.assertResponse(response, 200)
        self.assertEqual('1v1', response.json['match_type'])

        teams = ['Spectator', 'Spectator', 'Team B', 'Spectator', 'Spectator']
        for i in range(5):
            response = join_lobby(code, users[i], method='GET')
            self.assertResponse(response, 200)
            for user in response.json:
                if user['id'] == users[i]['id']:
                    self.assertEqual(teams[i], user['team'])
                    break


class Test05_UpdateParticipantLobby(UnitTest):

    def test_001_set_ready_to_true(self):
        user1 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        response = join_lobby(code, user1, data={'is_ready': True})
        self.assertResponse(response, 200)
        self.assertEqual(True, response.json['is_ready'])

    def test_002_change_team(self):
        user1 = new_user()

        response = create_lobby(user1, data={'game_mode': 'custom_game'})
        self.assertResponse(response, 201)
        code = response.json['code']

        response = join_lobby(code, user1, data={'team': 'Team B'})
        self.assertResponse(response, 200)
        self.assertEqual('Team B', response.json['team'])

        response = join_lobby(code, user1, data={'team': 'Spectator'})
        self.assertResponse(response, 200)
        self.assertEqual('Spectator', response.json['team'])

    def test_003_change_invalid_team(self):
        user1 = new_user()

        response = create_lobby(user1, data={'game_mode': 'custom_game'})
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user1, data={'team': 'Team caca'}), 400, {'team': ["Match type must be 'Team A', 'Team B' or 'Spectator'."]})

    def test_004_change_team_already_in(self):
        user1 = new_user()

        response = create_lobby(user1, data={'game_mode': 'custom_game'})
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user1, data={'team': 'Team A'}), 409, {'detail': 'You are already in this team.'})

    def test_005_change_team_full(self):
        user1 = new_user()
        user2 = new_user()

        response = create_lobby(user1, data={'game_mode': 'custom_game'})
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user2), 201)
        self.assertResponse(join_lobby(code, user2, data={'team': 'Team A'}, method='PATCH'), 403, {'detail': 'Team is full.'})


class Test06_LeaveLobby(UnitTest):

    def test_001_leave_lobby(self):
        user1 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user1, 'DELETE'), 204)
        self.assertResponse(join_lobby(code, user1, 'GET'), 403, {'detail': 'You do not belong to this lobby.'})
        self.assertResponse(create_lobby(user1, method='GET'), 404, {'detail': 'You do not belong to any lobby.'})

    def test_002_leave_lobby_then_other_member_became_creator(self):
        user1 = new_user()
        user2 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user2), 201)
        self.assertResponse(join_lobby(code, user1, 'DELETE'), 204)

        response = join_lobby(code, user2, 'GET')
        self.assertResponse(response, 200)
        self.assertEqual(1, len(response.json))
        self.assertEqual(True, response.json[0]['creator'])

    def test_003_guest_join_leave_lobby_then_destroy_lobby(self):
        user1 = new_user()
        user2 = guest_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user2), 201)
        self.assertResponse(join_lobby(code, user1, 'DELETE'), 204)
        self.assertResponse(join_lobby(code, user2, 'GET'), 403, {'detail': 'You do not belong to this lobby.'})
        self.assertResponse(create_lobby(user2, method='GET'), 404, {'detail': 'You do not belong to any lobby.'})

    def test_004_leave_lobby_does_not_exist(self):
        self.assertResponse(join_lobby('123456', method='DELETE'), 403, {'detail': 'You do not belong to this lobby.'})

    def test_005_leave_lobby_does_not_join(self):
        user1 = new_user()
        user2 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user2, 'DELETE'), 403, {'detail': 'You do not belong to this lobby.'})

    def test_006_leave_lobby_not_creator(self):
        user1 = new_user()
        user2 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user2), 201)
        self.assertResponse(join_lobby(code, user2, 'DELETE'), 204)

        response = join_lobby(code, user1, 'GET')
        self.assertResponse(response, 200)
        self.assertEqual(1, len(response.json))


class Test07_GetLobby(UnitTest):

    def test_001_get_lobby(self):
        user1 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        response = create_lobby(user1, method='GET')
        self.assertResponse(response, 200)
        self.assertEqual(code, response.json['code'])

    def test_002_get_lobby_does_not_join(self):
        self.assertResponse(create_lobby(method='GET'), 404, {'detail': 'You do not belong to any lobby.'})

    def test_002_get_lobby_participant(self):
        user1 = new_user()
        user2 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, user2), 201)

        response = join_lobby(code, user1, 'GET')
        self.assertResponse(response, 200)
        self.assertEqual(2, len(response.json))

    def test_003_get_lobby_participant_does_not_join(self):
        user1 = new_user()

        response = create_lobby(user1)
        self.assertResponse(response, 201)
        code = response.json['code']

        self.assertResponse(join_lobby(code, new_user(), 'GET'), 403, {'detail': 'You do not belong to this lobby.'})


if __name__ == '__main__':
    unittest.main()
