from services.blocked import blocked_user, unblocked_user
from services.tournament import create_tournament, join_tournament, kick_user, search_tournament
from utils.credentials import new_user, guest_user
from utils.generate_random import rnstr
from utils.my_unittest import UnitTest


class Test01_Tournament(UnitTest):

    def test_001_create_tournament(self):
        self.assertResponse(create_tournament(), 201)

    def test_002_join_tournament(self):
        code = self.assertResponse(create_tournament(), 201, get_id='code')

        self.assertResponse(join_tournament(code), 201)


class Test02_ErrorTournament(UnitTest):

    def test_001_tournament_does_not_exist(self):
        self.assertResponse(join_tournament('123456'), 404, {'detail': 'Tournament not found.'})

    def test_002_already_join(self):
        user1 = new_user()
        user2 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(join_tournament(code, user2), 201)
        self.assertResponse(join_tournament(code, user1), 409, {'detail': 'You already joined this tournament.'})
        self.assertResponse(join_tournament(code, user2), 409, {'detail': 'You already joined this tournament.'})

    def test_003_tournament_is_full(self):
        code = self.assertResponse(create_tournament(), 201, get_id='code')

        for _ in range(3):
            self.assertResponse(join_tournament(code), 201)
        self.assertResponse(join_tournament(code), 403, {'detail': 'Tournament already started.'})
        # self.assertResponse(join_tournament(code), 403, {'detail': 'Tournament is full.'}) todo make

    def test_004_tournament_is_already_started(self):
        code = self.assertResponse(create_tournament(), 201, get_id='code')

        for _ in range(3):
            self.assertResponse(join_tournament(code), 201)

        self.assertResponse(join_tournament(code), 403, {'detail': 'Tournament already started.'})

    def test_005_guest_create_tournament(self):
        self.assertResponse(create_tournament(guest_user()), 403, {'detail': 'Guest users cannot create tournament.'})

    def test_006_no_name(self):
        self.assertResponse(create_tournament(data={}), 400, {'name': ['This field is required.']})

    def test_007_blocked_user_cannot_join(self):
        user1 = new_user()
        user2 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(blocked_user(user1, user2['id']), 201)
        self.assertResponse(join_tournament(code, user2), 404, {'detail': 'Tournament not found.'})

    def test_008_blocked_user_kick_user(self):
        user1 = new_user()
        user2 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(join_tournament(code, user2), 201)
        self.assertResponse(blocked_user(user1, user2['id']), 201)

        response = join_tournament(code, user1, 'GET')
        self.assertResponse(response, 200)
        self.assertEqual(1, len(response.json))

        self.assertResponse(create_tournament(user2, method='GET'), 404, {'detail': 'You do not belong to any tournament.'})

    def test_009_blocked_user_not_creator(self):
        user1 = new_user()
        user2 = new_user()
        user3 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(join_tournament(code, user2), 201)
        self.assertResponse(join_tournament(code, user3), 201)
        self.assertResponse(blocked_user(user2, user3['id']), 201)

        response = join_tournament(code, user1, 'GET')
        self.assertResponse(response, 200)
        self.assertEqual(3, len(response.json))

    def test_010_create_two_tournament(self):
        user1 = new_user()

        self.assertResponse(create_tournament(user1), 201)
        self.assertResponse(create_tournament(user1), 403, {'detail': 'You cannot create more than one tournament at the same time.'})

    def test_011_create_two_tournament_leave_first(self):
        user1 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')
        self.assertResponse(join_tournament(code), 201)

        self.assertResponse(join_tournament(code, user1, 'DELETE'), 204)
        self.assertResponse(create_tournament(user1), 403, {'detail': 'You cannot create more than one tournament at the same time.'})

    def test_012_blocked_then_unblock(self):
        user1 = new_user()
        user2 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(join_tournament(code, user2), 201)
        blocked_id = self.assertResponse(blocked_user(user1, user2['id']), 201, get_id=True)

        response = join_tournament(code, user1, 'GET')
        self.assertResponse(response, 200)
        self.assertEqual(1, len(response.json))

        self.assertResponse(join_tournament(code, user2), 404, {'detail': 'Tournament not found.'})
        self.assertResponse(unblocked_user(user1, blocked_id), 204)
        self.assertResponse(join_tournament(code, user2), 201)


class Test03_KickTournament(UnitTest):

    def test_001_kick_tournament(self):
        user1 = new_user()
        user2 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(join_tournament(code, user2), 201)
        self.assertResponse(kick_user(user1, user2, code), 204)

        response = join_tournament(code, user1, 'GET')
        self.assertResponse(response, 200)
        self.assertEqual(1, len(response.json))

    def test_002_user_kick_not_join_tournament(self):
        user1 = new_user()
        user2 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(kick_user(user2, user1, code), 403, {'detail': 'You do not belong to this tournament.'})

    def test_003_user_kicked_not_join_tournament(self):
        user1 = new_user()
        user2 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(kick_user(user1, user2, code), 404, {'detail': 'This user does not belong to this tournament.'})

    def test_004_invalid_tournament(self):
        self.assertResponse(kick_user(new_user(), new_user(), '123456'), 403, {'detail': 'You do not belong to this tournament.'})

    def test_005_not_creator(self):
        user1 = new_user()
        user2 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(join_tournament(code, user2), 201)
        self.assertResponse(kick_user(user2, user1, code), 403, {'detail': 'Only creator can update this tournament.'})

    def test_006_users_does_exist(self):
        user1 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(kick_user(user1, {'id': 123456789}, code), 404, {'detail': 'This user does not belong to this tournament.'})


class Test04_UpdateTournament(UnitTest):

    def test_001_update_tournament(self):
        user1 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(create_tournament(user1, {'size': 12, 'name': 'coucou'}, 'PATCH'), 405, {'detail': 'Method "PATCH" not allowed.'})


class Test05_UpdateParticipantTournament(UnitTest):

    def test_001_update_participant(self):
        user1 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(join_tournament(code, user1, data={'index': 2}), 405, {'detail': 'Method "PATCH" not allowed.'})


class Test06_LeaveTournament(UnitTest):

    def test_001_leave_tournament_then_destroy(self):
        user1 = new_user()
        users = [new_user() for _ in range(2)]

        response = create_tournament(user1)
        code = self.assertResponse(response, 201, get_id='code')
        name = response.json['name']

        for u in users:
            self.assertResponse(join_tournament(code, u), 201)

        self.assertResponse(join_tournament(code, user1, 'DELETE'), 204)
        self.assertResponse(join_tournament(code, user1, 'GET'), 403, {'detail': 'You do not belong to this tournament.'})
        self.assertResponse(create_tournament(user1, method='GET'), 404, {'detail': 'You do not belong to any tournament.'})

        self.assertResponse(search_tournament(name, user1), 200, count=1)

        for u in users:
            self.assertResponse(join_tournament(code, u, 'GET'), 200)

        for u in users:
            self.assertResponse(join_tournament(code, u, 'DELETE'), 204)
            self.assertResponse(join_tournament(code, u, 'GET'), 403, {'detail': 'You do not belong to this tournament.'})
            self.assertResponse(create_tournament(u, method='GET'), 404, {'detail': 'You do not belong to any tournament.'})

        self.assertResponse(search_tournament(name, user1), 200, count=0)

    def test_002_leave_tournament(self):
        user1 = new_user()
        user2 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(join_tournament(code, user2), 201)
        self.assertResponse(join_tournament(code, user1, 'DELETE'), 204)

        response = join_tournament(code, user2, 'GET')
        self.assertResponse(response, 200)
        self.assertEqual(1, len(response.json))

    def test_004_leave_tournament_does_not_exist(self):
        self.assertResponse(join_tournament('123456', method='DELETE'), 403, {'detail': 'You do not belong to this tournament.'})

    def test_005_leave_tournament_does_not_join(self):
        user1 = new_user()
        user2 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(join_tournament(code, user2, 'DELETE'), 403, {'detail': 'You do not belong to this tournament.'})

    def test_006_leave_tournament_not_creator(self):
        user1 = new_user()
        user2 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(join_tournament(code, user2), 201)
        self.assertResponse(join_tournament(code, user2, 'DELETE'), 204)

        response = join_tournament(code, user1, 'GET')
        self.assertResponse(response, 200)
        self.assertEqual(1, len(response.json))

    def test_007_leave_tournament_then_come_back_still_creator(self):
        user1 = new_user()
        user2 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(join_tournament(code, user2), 201)

        self.assertResponse(join_tournament(code, user1, 'DELETE'), 204)

        response = join_tournament(code, user1)
        self.assertResponse(response, 201)
        for u in response.json['participants']:
            if u['id'] == user1['id']:
                self.assertTrue(u['creator'])
                break


class Test07_GetTournament(UnitTest):

    def test_001_get_tournament(self):
        user1 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        response = create_tournament(user1, method='GET')
        self.assertResponse(response, 200)
        self.assertEqual(code, response.json['code'])

    def test_002_get_tournament_does_not_join(self):
        self.assertResponse(create_tournament(method='GET'), 404, {'detail': 'You do not belong to any tournament.'})

    def test_002_get_tournament_participant(self):
        user1 = new_user()
        user2 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(join_tournament(code, user2), 201)

        response = join_tournament(code, user1, 'GET')
        self.assertResponse(response, 200)
        self.assertEqual(2, len(response.json))

    def test_003_get_tournament_participant_does_not_join(self):
        user1 = new_user()

        code = self.assertResponse(create_tournament(user1), 201, get_id='code')

        self.assertResponse(join_tournament(code, new_user(), 'GET'), 403, {'detail': 'You do not belong to this tournament.'})

    def test_004_search_tournaments(self):
        user1 = new_user()
        name = rnstr()

        for i in range(5):
            self.assertResponse(create_tournament(new_user(), data={'name': 'Tournoi ' + name + rnstr()}), 201)

        self.assertResponse(create_tournament(new_user(), data={'name': 'coucou' + name}), 201)

        self.assertResponse(search_tournament('coucou' + name, user1), 200, count=1)

        self.assertResponse(search_tournament('Tournoi ' + name, user1), 200, count=5)

    def test_005_search_private_tournament(self):
        user1 = new_user()
        user2 = new_user()

        self.assertResponse(create_tournament(user1, data={'name': 'private' + rnstr(), 'private': True}), 201)

        self.assertResponse(search_tournament('private', user2), 200, count=0)

        self.assertResponse(search_tournament('private', user1), 200, count=1)

    def test_006_search_tournament_none(self):
        self.assertResponse(search_tournament('caca'), 200, count=0)

    def test_007_search_tournaments_blocked_by_creator_tournament(self):
        user1 = new_user()
        user2 = new_user()
        name = rnstr()

        self.assertResponse(create_tournament(user1, data={'name': 'Blocked ' + name + rnstr()}), 201)
        blocked_id = self.assertResponse(blocked_user(user1, user2['id']), 201)
        self.assertResponse(search_tournament('Blocked ' + name, user2), 200, count=0)
        self.assertResponse(unblocked_user(user1, blocked_id), 204)
        self.assertResponse(search_tournament('Blocked ' + name, user2), 200, count=5)


# todo test start after make it
# todo test leave tournament after start
# todo test stage
# todo test index after make it
# todo test when tournament ended
# todo test search user block does not appear
if __name__ == '__main__':
    unittest.main()
