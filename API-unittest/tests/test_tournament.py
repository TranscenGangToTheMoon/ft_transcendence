import unittest

from services.blocked import blocked_user, unblocked_user
from services.tournament import create_tournament, join_tournament, ban_user, search_tournament
from utils.generate_random import rnstr
from utils.my_unittest import UnitTest


# todo  si pas connecter tu peux pas jouer matchmaking


class Test01_Tournament(UnitTest):

    def test_001_create_tournament(self):
        user1 = self.user_sse()

        self.assertResponse(create_tournament(user1), 201)
        self.assertThread(user1)

    def test_002_join_tournament(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')
        self.assertResponse(join_tournament(user2, code), 201)
        self.assertThread(user2)
        self.assertThread(user1)


class Test02_ErrorTournament(UnitTest):

    def test_001_tournament_does_not_exist(self):
        user1 = self.user_sse()

        self.assertResponse(join_tournament(user1, '123456'), 404, {'detail': 'Tournament not found.'})
        self.assertThread(user1)

    def test_002_already_join(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(join_tournament(user1, code), 409, {'detail': 'You already joined this tournament.'})
        self.assertResponse(join_tournament(user2, code), 409, {'detail': 'You already joined this tournament.'})
        self.assertThread(user2)
        self.assertThread(user1)

    def test_003_tournament_is_full(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        for _ in range(3):
            user_tmp = self.user_sse()
            self.assertResponse(join_tournament(user_tmp, code), 201)
        self.assertResponse(join_tournament(user1, code), 403, {'detail': 'Tournament already started.'})
        # self.assertResponse(join_tournament(code, self.user_sse()()), 403, {'detail': 'Tournament is full.'}) todo make when tournament work
        self.assertThread(user2)
        self.assertThread(user1)

    def test_004_tournament_is_already_started(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        for _ in range(3):
            user_tmp = self.user_sse()
            self.assertResponse(join_tournament(user_tmp, code), 201)

        self.assertResponse(join_tournament(user2, code), 403, {'detail': 'Tournament already started.'})
        self.assertThread(user2)
        self.assertThread(user1)

    def test_005_guest_create_tournament(self):
        user1 = self.guest_user()

        self.assertResponse(create_tournament(user1), 403, {'detail': 'Guest users cannot create tournament.'})
        self.assertThread(user1)

    def test_006_no_name(self):
        user1 = self.user_sse()

        self.assertResponse(create_tournament(user1, data={}), 400, {'name': ['This field is required.']})
        self.assertThread(user1)

    def test_007_blocked_user_cannot_join(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(blocked_user(user1, user2['id']), 201)
        self.assertResponse(join_tournament(user2, code), 404, {'detail': 'Tournament not found.'})
        self.assertThread(user2)
        self.assertThread(user1)

    def test_008_blocked_user_ban_user(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(blocked_user(user1, user2['id']), 201)

        response = self.assertResponse(join_tournament(user1, code, 'GET'), 200)
        self.assertEqual(1, len(response))

        self.assertResponse(create_tournament(user2, method='GET'), 404, {'detail': 'You do not belong to any tournament.'})
        self.assertThread(user2)
        self.assertThread(user1)

    def test_009_blocked_user_not_creator(self):
        user1 = self.user_sse()
        user2 = self.user_sse()
        user3 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(join_tournament(user3, code), 201)
        self.assertResponse(blocked_user(user2, user3['id']), 201)

        response = self.assertResponse(join_tournament(user1, code, 'GET'), 200)
        self.assertEqual(3, len(response))
        self.assertThread(user3)
        self.assertThread(user2)
        self.assertThread(user1)

    def test_010_create_two_tournament(self):
        user1 = self.user_sse()

        self.assertResponse(create_tournament(user1), 201)
        self.assertResponse(create_tournament(user1), 403, {'detail': 'You cannot create more than one tournament at the same time.'})
        self.assertThread(user1)

    def test_011_create_two_tournament_leave_first(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')
        self.assertResponse(join_tournament(user2, code), 201)

        self.assertResponse(join_tournament(user1, code, 'DELETE'), 204)
        self.assertResponse(create_tournament(user1), 403, {'detail': 'You cannot create more than one tournament at the same time.'})
        self.assertThread(user2)
        self.assertThread(user1)

    def test_012_blocked_then_unblock(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        blocked_id = self.assertResponse(blocked_user(user1, user2['id']), 201, get_field=True)

        response = self.assertResponse(join_tournament(user1, code, 'GET'), 200)
        self.assertEqual(1, len(response))

        self.assertResponse(join_tournament(user2, code), 404, {'detail': 'Tournament not found.'})
        self.assertResponse(unblocked_user(user1, blocked_id), 204)
        self.assertResponse(join_tournament(user2, code), 201)
        self.assertThread(user2)
        self.assertThread(user1)


class Test03_BanTournament(UnitTest):

    def test_001_ban_tournament(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(ban_user(user1, user2, code), 204)

        response = self.assertResponse(join_tournament(user1, code, 'GET'), 200)
        self.assertEqual(1, len(response))
        self.assertThread(user2)
        self.assertThread(user1)

    def test_002_user_ban_not_join_tournament(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(ban_user(user2, user1, code), 403, {'detail': 'You do not belong to this tournament.'})
        self.assertThread(user2)
        self.assertThread(user1)

    def test_003_user_baned_not_join_tournament(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(ban_user(user1, user2, code), 404, {'detail': 'This user does not belong to this tournament.'})
        self.assertThread(user2)
        self.assertThread(user1)

    def test_004_invalid_tournament(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        self.assertResponse(ban_user(user1, user2, '123456'), 403, {'detail': 'You do not belong to this tournament.'})
        self.assertThread(user2)
        self.assertThread(user1)

    def test_005_not_creator(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(ban_user(user2, user1, code), 403, {'detail': 'Only creator can update this tournament.'})
        self.assertThread(user2)
        self.assertThread(user1)

    def test_006_users_does_exist(self):
        user1 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(ban_user(user1, {'id': 123456789}, code), 404, {'detail': 'This user does not belong to this tournament.'})
        self.assertThread(user1)


class Test04_UpdateTournament(UnitTest):

    def test_001_update_tournament(self):
        user1 = self.user_sse()

        self.assertResponse(create_tournament(user1, {'size': 12, 'name': 'coucou'}, 'PATCH'), 405, {'detail': 'Method "PATCH" not allowed.'})
        self.assertThread(user1)


class Test05_UpdateParticipantTournament(UnitTest):

    def test_001_update_participant(self):
        user1 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user1, code, data={'index': 2}), 405, {'detail': 'Method "PATCH" not allowed.'})
        self.assertThread(user1)


class Test06_LeaveTournament(UnitTest):

    def test_001_leave_tournament_then_destroy(self):
        user1 = self.user_sse()
        users = [self.user_sse() for _ in range(2)]

        response = self.assertResponse(create_tournament(user1), 201)
        code = response['code']
        name = response['name']

        for u in users:
            self.assertResponse(join_tournament(u, code), 201)

        self.assertResponse(join_tournament(user1, code, 'DELETE'), 204)
        self.assertResponse(join_tournament(user1, code, 'GET'), 403, {'detail': 'You do not belong to this tournament.'})
        self.assertResponse(create_tournament(user1, method='GET'), 404, {'detail': 'You do not belong to any tournament.'})

        self.assertResponse(search_tournament(user1, name), 200, count=1)

        for u in users:
            self.assertResponse(join_tournament(u, code, 'GET'), 200)

        for u in users:
            self.assertResponse(join_tournament(u, code, 'DELETE'), 204)
            self.assertResponse(join_tournament(u, code, 'GET'), 403, {'detail': 'You do not belong to this tournament.'})
            self.assertResponse(create_tournament(u, method='GET'), 404, {'detail': 'You do not belong to any tournament.'})

        self.assertResponse(search_tournament(user1, name), 200, count=0)
        [self.assertThread(u) for u in users]
        self.assertThread(user1)

    def test_002_leave_tournament(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(join_tournament(user1, code, 'DELETE'), 204)

        response = self.assertResponse(join_tournament(user2, code, 'GET'), 200)
        self.assertEqual(1, len(response))
        self.assertThread(user2)
        self.assertThread(user1)

    def test_004_leave_tournament_does_not_exist(self):
        user1 = self.user_sse()

        self.assertResponse(join_tournament(user1, '123456', method='DELETE'), 403, {'detail': 'You do not belong to this tournament.'})
        self.assertThread(user1)

    def test_005_leave_tournament_does_not_join(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code, 'DELETE'), 403, {'detail': 'You do not belong to this tournament.'})
        self.assertThread(user2)
        self.assertThread(user1)

    def test_006_leave_tournament_not_creator(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(join_tournament(user2, code, 'DELETE'), 204)

        response = self.assertResponse(join_tournament(user1, code, 'GET'), 200)
        self.assertEqual(1, len(response))
        self.assertThread(user2)
        self.assertThread(user1)

    def test_007_leave_tournament_then_come_back_still_creator(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)

        self.assertResponse(join_tournament(user1, code, 'DELETE'), 204)

        response = self.assertResponse(join_tournament(user1, code), 201)
        for u in response['participants']:
            if u['id'] == user1['id']:
                self.assertTrue(u['creator'])
                break
        self.assertThread(user2)
        self.assertThread(user1)


class Test07_GetTournament(UnitTest):

    def test_001_get_tournament(self):
        user1 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        response = self.assertResponse(create_tournament(user1, method='GET'), 200)
        self.assertEqual(code, response['code'])
        self.assertThread(user1)

    def test_002_get_tournament_does_not_join(self):
        user1 = self.user_sse()

        self.assertResponse(create_tournament(user1, method='GET'), 404, {'detail': 'You do not belong to any tournament.'})
        self.assertThread(user1)

    def test_002_get_tournament_participant(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)

        response = self.assertResponse(join_tournament(user1, code, 'GET'), 200)
        self.assertEqual(2, len(response))
        self.assertThread(user2)
        self.assertThread(user1)

    def test_003_get_tournament_participant_does_not_join(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code, 'GET'), 403, {'detail': 'You do not belong to this tournament.'})
        self.assertThread(user2)
        self.assertThread(user1)

    def test_004_search_tournaments(self):
        user1 = self.user_sse()
        user2 = self.user_sse()
        name = rnstr()
        users = [self.user_sse() for _ in range(5)]

        for user_tmp in users:
            self.assertResponse(create_tournament(user_tmp, data={'name': 'Tournoi ' + name + rnstr()}), 201)

        self.assertResponse(create_tournament(user2, data={'name': 'coucou' + name}), 201)

        self.assertResponse(search_tournament(user1, 'coucou' + name), 200, count=1)

        self.assertResponse(search_tournament(user1, 'Tournoi ' + name), 200, count=5)
        [self.assertThread(u) for u in users]
        self.assertThread(user2)
        self.assertThread(user1)

    def test_005_search_private_tournament(self):
        user1 = self.user_sse()
        user2 = self.user_sse()

        self.assertResponse(create_tournament(user1, data={'name': 'private' + rnstr(), 'private': True}), 201)

        self.assertResponse(search_tournament(user2, 'private'), 200, count=0)

        self.assertResponse(search_tournament(user1, 'private'), 200, count=1)
        self.assertThread(user2)
        self.assertThread(user1)

    def test_006_search_tournament_none(self):
        user1 = self.user_sse()

        self.assertResponse(search_tournament(user1, 'caca'), 200, count=0)
        self.assertThread(user1)

    def test_007_search_tournaments_blocked_by_creator_tournament(self):
        user1 = self.user_sse()
        user2 = self.user_sse()
        user3 = self.user_sse()
        name = rnstr()

        self.assertResponse(create_tournament(user3, data={'name': 'Blocked ' + name + rnstr()}), 201)
        self.assertResponse(create_tournament(user1, data={'name': 'Blocked ' + name + rnstr()}), 201)
        blocked_id = self.assertResponse(blocked_user(user1, user2['id']), 201, get_field=True)
        self.assertResponse(search_tournament(user2, 'Blocked ' + name), 200, count=1)
        self.assertResponse(unblocked_user(user1, blocked_id), 204)
        self.assertResponse(search_tournament(user2, 'Blocked ' + name), 200, count=2)
        self.assertThread(user3)
        self.assertThread(user2)
        self.assertThread(user1)

    def test_008_search_tournaments_blocked_by_user_tournament(self):
        user1 = self.user_sse()
        user2 = self.user_sse()
        user3 = self.user_sse()
        name = rnstr()

        self.assertResponse(create_tournament(user3, data={'name': 'Blocked ' + name + rnstr()}), 201)
        self.assertResponse(create_tournament(user1, data={'name': 'Blocked ' + name + rnstr()}), 201)
        blocked_id = self.assertResponse(blocked_user(user2, user1['id']), 201, get_field=True)
        self.assertResponse(search_tournament(user2, 'Blocked ' + name), 200, count=1)
        self.assertResponse(unblocked_user(user2, blocked_id), 204)
        self.assertResponse(search_tournament(user2, 'Blocked ' + name), 200, count=2)
        self.assertThread(user3)
        self.assertThread(user2)
        self.assertThread(user1)


# todo test start after make it
# todo test leave tournament after start
# todo test stage
# todo test index after make it
# todo test when tournament ended

if __name__ == '__main__':
    unittest.main()
