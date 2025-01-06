import time
import unittest

from services.blocked import blocked_user, unblocked_user
from services.friend import create_friendship
from services.game import score
from services.tournament import create_tournament, join_tournament, ban_user, search_tournament, invite_user
from utils.generate_random import rnstr
from utils.my_unittest import UnitTest


class Test01_Tournament(UnitTest):

    def test_001_create_tournament(self):
        user1 = self.user()

        self.assertResponse(create_tournament(user1), 201)
        self.assertThread(user1)

    def test_002_join_tournament(self):
        user1 = self.user(['tournament-join'])
        user2 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')
        self.assertResponse(join_tournament(user2, code), 201)
        self.assertThread(user1, user2)

    def test_003_join_two_tournament(self):
        user1 = self.user(['tournament-join', 'tournament-leave'])
        user2 = self.user()
        user3 = self.user(['tournament-join'])

        code1 = self.assertResponse(create_tournament(user1), 201, get_field='code')
        code2 = self.assertResponse(create_tournament(user3), 201, get_field='code')
        self.assertResponse(join_tournament(user2, code1), 201)
        self.assertResponse(join_tournament(user2, code1, method='DELETE'), 204)
        self.assertResponse(join_tournament(user2, code2), 201)
        self.assertThread(user1, user2, user3)


class Test02_ErrorTournament(UnitTest):

    def test_001_tournament_does_not_exist(self):
        user1 = self.user()

        self.assertResponse(join_tournament(user1, '123456'), 404, {'detail': 'Tournament not found.'})
        self.assertThread(user1)

    def test_002_already_join(self):
        user1 = self.user(['tournament-join'])
        user2 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(join_tournament(user1, code), 409, {'detail': 'You already joined this tournament.'})
        self.assertResponse(join_tournament(user2, code), 409, {'detail': 'You already joined this tournament.'})
        self.assertThread(user1, user2)

    def test_003_tournament_is_full(self):
        user1 = self.user(['tournament-join'] * 3)
        user2 = self.user()
        users = [self.user(['tournament-join'] * (2 - i)) for i in range(3)]

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        for user_tmp in users:
            self.assertResponse(join_tournament(user_tmp, code), 201)
        self.assertResponse(join_tournament(user2, code), 403, {'detail': 'Tournament already started.'})
        self.assertThread(user1, user2, *users)

    def test_004_guest_create_tournament(self):
        user1 = self.user(guest=True)

        self.assertResponse(create_tournament(user1), 403, {'detail': 'Guest users cannot perform this action.'})
        self.assertThread(user1)

    def test_005_no_name(self):
        user1 = self.user()

        self.assertResponse(create_tournament(user1, data={}), 400, {'name': ['This field is required.']})
        self.assertThread(user1)

    def test_006_blocked_user_cannot_join(self):
        user1 = self.user()
        user2 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(blocked_user(user1, user2['id']), 201)
        self.assertResponse(join_tournament(user2, code), 404, {'detail': 'Tournament not found.'})
        self.assertThread(user1, user2)

    def test_007_blocked_user(self):
        user1 = self.user(['tournament-join', 'tournament-leave'])
        user2 = self.user(['tournament-banned'])

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(blocked_user(user1, user2['id']), 201)

        response = self.assertResponse(join_tournament(user1, code, 'GET'), 200)
        self.assertEqual(1, len(response))

        self.assertResponse(create_tournament(user2, method='GET'), 404, {'detail': 'You do not belong to any tournament.'})
        self.assertThread(user1, user2)

    def test_008_blocked_user_not_creator(self):
        user1 = self.user(['tournament-join', 'tournament-join'])
        user2 = self.user(['tournament-join'])
        user3 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(join_tournament(user3, code), 201)
        self.assertResponse(blocked_user(user2, user3['id']), 201)

        response = self.assertResponse(join_tournament(user1, code, 'GET'), 200)
        self.assertEqual(3, len(response))
        self.assertThread(user1, user2, user3)

    def test_009_blocked_then_unblock(self):
        user1 = self.user(['tournament-join', 'tournament-leave', 'tournament-join'])
        user2 = self.user(['tournament-banned'])

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        blocked_id = self.assertResponse(blocked_user(user1, user2['id']), 201, get_field=True)

        response = self.assertResponse(join_tournament(user1, code, 'GET'), 200)
        self.assertEqual(1, len(response))

        self.assertResponse(join_tournament(user2, code), 404, {'detail': 'Tournament not found.'})
        self.assertResponse(unblocked_user(user1, blocked_id), 204)
        self.assertResponse(join_tournament(user2, code), 201)
        self.assertThread(user1, user2)

    def test_011_create_two_tournament(self):
        user1 = self.user()

        self.assertResponse(create_tournament(user1), 201)
        self.assertResponse(create_tournament(user1), 403, {'detail': 'You cannot create more than one tournament at the same time.'})
        self.assertThread(user1)

    def test_012_create_two_tournament_leave_first(self):
        user1 = self.user(['tournament-join'])
        user2 = self.user(['tournament-leave'])

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')
        self.assertResponse(join_tournament(user2, code), 201)

        self.assertResponse(join_tournament(user1, code, 'DELETE'), 204)
        self.assertResponse(create_tournament(user1), 403, {'detail': 'You cannot create more than one tournament at the same time.'})
        self.assertResponse(join_tournament(user2, code, 'DELETE'), 204)
        self.assertResponse(create_tournament(user1), 201)
        self.assertThread(user1, user2)

    def test_013_join_tournament_without_sse(self):
        user1 = self.user(sse=False)
        user2 = self.user()

        self.assertResponse(create_tournament(user1), 401, {'code': 'sse_connection_required', 'detail': 'You need to be connected to SSE to access this resource.'})
        code = self.assertResponse(create_tournament(user2), 201, get_field='code')
        self.assertResponse(join_tournament(user1, code), 401, {'code': 'sse_connection_required', 'detail': 'You need to be connected to SSE to access this resource.'})
        self.assertThread(user2)


class Test03_BanTournament(UnitTest):

    def test_001_ban_tournament(self):
        user1 = self.user(['tournament-join', 'tournament-leave'])
        user2 = self.user(['tournament-banned'])

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(ban_user(user1, user2, code), 204)
        self.assertResponse(join_tournament(user2, code), 404, {'detail': 'Tournament not found.'})

        response = self.assertResponse(join_tournament(user1, code, 'GET'), 200)
        self.assertEqual(1, len(response))
        self.assertThread(user1, user2)

    def test_002_user_ban_not_join_tournament(self):
        user1 = self.user()
        user2 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(ban_user(user2, user1, code), 403, {'detail': 'You do not belong to this tournament.'})
        self.assertThread(user1, user2)

    def test_003_user_banned_not_join_tournament(self):
        user1 = self.user()
        user2 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(ban_user(user1, user2, code), 404, {'detail': 'This user does not belong to this tournament.'})
        self.assertThread(user1, user2)

    def test_004_invalid_tournament(self):
        user1 = self.user()
        user2 = self.user()

        self.assertResponse(ban_user(user1, user2, '123456'), 403, {'detail': 'You do not belong to this tournament.'})
        self.assertThread(user1, user2)

    def test_005_not_creator(self):
        user1 = self.user(['tournament-join'])
        user2 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(ban_user(user2, user1, code), 403, {'detail': 'Only creator can update this tournament.'}) # todo pas bonne reponse
        self.assertThread(user1, user2)

    def test_006_users_does_exist(self):
        user1 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(ban_user(user1, {'id': 123456789}, code), 404, {'detail': 'This user does not belong to this tournament.'})
        self.assertThread(user1)


class Test04_UpdateTournament(UnitTest):

    def test_001_update_tournament(self):
        user1 = self.user()

        self.assertResponse(create_tournament(user1, {'size': 12, 'name': 'coucou'}, 'PATCH'), 405, {'detail': 'Method "PATCH" not allowed.'})
        self.assertThread(user1)


class Test05_UpdateParticipantTournament(UnitTest):

    def test_001_update_participant(self):
        user1 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user1, code, data={'index': 2}), 405, {'detail': 'Method "PATCH" not allowed.'})
        self.assertThread(user1)


class Test06_LeaveTournament(UnitTest):

    def test_001_leave_tournament_then_destroy(self):
        user1 = self.user(['tournament-join', 'tournament-join'])
        users = [self.user(['tournament-join'] * (1 - i) + ['tournament-leave'] * (i + 1)) for i in range(2)]

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
        self.assertThread(user1, *users)

    def test_002_leave_tournament(self):
        user1 = self.user(['tournament-join'])
        user2 = self.user(['tournament-leave'])

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(join_tournament(user1, code, 'DELETE'), 204)

        response = self.assertResponse(join_tournament(user2, code, 'GET'), 200)
        self.assertEqual(1, len(response))
        self.assertThread(user1, user2)

    def test_004_leave_tournament_does_not_exist(self):
        user1 = self.user()

        self.assertResponse(join_tournament(user1, '123456', method='DELETE'), 403, {'detail': 'You do not belong to this tournament.'})
        self.assertThread(user1)

    def test_005_leave_tournament_does_not_join(self):
        user1 = self.user()
        user2 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code, 'DELETE'), 403, {'detail': 'You do not belong to this tournament.'})
        self.assertThread(user1, user2)

    def test_006_leave_tournament_not_creator(self):
        user1 = self.user(['tournament-join', 'tournament-leave'])
        user2 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(join_tournament(user2, code, 'DELETE'), 204)

        response = self.assertResponse(join_tournament(user1, code, 'GET'), 200)
        self.assertEqual(1, len(response))
        self.assertThread(user1, user2)

    def test_007_leave_tournament_then_come_back_still_creator(self):
        user1 = self.user(['tournament-join'])
        user2 = self.user(['tournament-leave', 'tournament-join'])

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)

        self.assertResponse(join_tournament(user1, code, 'DELETE'), 204)

        response = self.assertResponse(join_tournament(user1, code), 201)
        for u in response['participants']:
            if u['id'] == user1['id']:
                self.assertTrue(u['creator'])
                break
        self.assertThread(user1, user2)


class Test07_GetTournament(UnitTest):

    def test_001_get_tournament(self):
        user1 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        response = self.assertResponse(create_tournament(user1, method='GET'), 200)
        self.assertEqual(code, response['code'])
        self.assertThread(user1)

    def test_002_get_tournament_does_not_join(self):
        user1 = self.user()

        self.assertResponse(create_tournament(user1, method='GET'), 404, {'detail': 'You do not belong to any tournament.'})
        self.assertThread(user1)

    def test_002_get_tournament_participant(self):
        user1 = self.user(['tournament-join'])
        user2 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code), 201)

        response = self.assertResponse(join_tournament(user1, code, 'GET'), 200)
        self.assertEqual(2, len(response))
        self.assertThread(user1, user2)

    def test_003_get_tournament_participant_does_not_join(self):
        user1 = self.user()
        user2 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')

        self.assertResponse(join_tournament(user2, code, 'GET'), 403, {'detail': 'You do not belong to this tournament.'})
        self.assertThread(user1, user2)

    def test_004_search_tournaments(self):
        user1 = self.user()
        user2 = self.user()
        name = rnstr()
        users = [self.user() for _ in range(5)]

        for user_tmp in users:
            self.assertResponse(create_tournament(user_tmp, data={'name': 'Tournoi ' + name + rnstr()}), 201)

        self.assertResponse(create_tournament(user2, data={'name': 'coucou' + name}), 201)

        self.assertResponse(search_tournament(user1, 'coucou' + name), 200, count=1)

        self.assertResponse(search_tournament(user1, 'Tournoi ' + name), 200, count=5)
        [self.assertThread(u) for u in users]
        self.assertThread(user1, user2)

    def test_005_search_private_tournament(self):
        user1 = self.user()
        user2 = self.user()

        self.assertResponse(create_tournament(user1, data={'name': 'private' + rnstr(), 'private': True}), 201)

        self.assertResponse(search_tournament(user2, 'private'), 200, count=0)

        self.assertResponse(search_tournament(user1, 'private'), 200, count=1)
        self.assertThread(user1, user2)

    def test_006_search_tournament_none(self):
        user1 = self.user()

        self.assertResponse(search_tournament(user1, 'caca'), 200, count=0)
        self.assertThread(user1)

    def test_007_search_tournaments_blocked_by_creator_tournament(self):
        user1 = self.user()
        user2 = self.user()
        user3 = self.user()
        name = rnstr()

        self.assertResponse(create_tournament(user3, data={'name': 'Blocked ' + name + rnstr()}), 201)
        self.assertResponse(create_tournament(user1, data={'name': 'Blocked ' + name + rnstr()}), 201)
        blocked_id = self.assertResponse(blocked_user(user1, user2['id']), 201, get_field=True)
        self.assertResponse(search_tournament(user2, 'Blocked ' + name), 200, count=1)
        self.assertResponse(unblocked_user(user1, blocked_id), 204)
        self.assertResponse(search_tournament(user2, 'Blocked ' + name), 200, count=2)
        self.assertThread(user3, user1, user1)

    def test_008_search_tournaments_blocked_by_user_tournament(self):
        user1 = self.user()
        user2 = self.user()
        user3 = self.user()
        name = rnstr()

        self.assertResponse(create_tournament(user3, data={'name': 'Blocked ' + name + rnstr()}), 201)
        self.assertResponse(create_tournament(user1, data={'name': 'Blocked ' + name + rnstr()}), 201)
        blocked_id = self.assertResponse(blocked_user(user2, user1['id']), 201, get_field=True)
        self.assertResponse(search_tournament(user2, 'Blocked ' + name), 200, count=1)
        self.assertResponse(unblocked_user(user2, blocked_id), 204)
        self.assertResponse(search_tournament(user2, 'Blocked ' + name), 200, count=2)
        self.assertThread(user3, user1, user1)


class Test08_InviteTournament(UnitTest):

    def test_001_invite(self):
        user1 = self.user(['accept-friend-request', 'tournament-join'])
        user2 = self.user(['accept-friend-request'])
        user3 = self.user(['receive-friend-request', 'invite-tournament'])
        user4 = self.user(['receive-friend-request', 'invite-tournament'])

        self.assertFriendResponse(create_friendship(user1, user3))
        self.assertFriendResponse(create_friendship(user2, user4))
        code = self.assertResponse(create_tournament(user1), 201, get_field='code')
        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(invite_user(user1, user3, code), 204)
        self.assertResponse(invite_user(user2, user4, code), 204)
        self.assertThread(user1, user2)

    def test_004_invite_yourself(self):
        user1 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')
        self.assertResponse(invite_user(user1, user1, code), 403, {'detail': 'You cannot invite yourself.'})
        self.assertThread(user1)

    def test_005_not_friend(self):
        user1 = self.user()
        user2 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')
        self.assertResponse(invite_user(user1, user2, code), 403, {'detail': 'You can only invite friends.'})
        self.assertThread(user1, user2)

    def test_006_not_creator_private_tournament(self):
        user1 = self.user(['tournament-join'])
        user2 = self.user()
        user3 = self.user()

        code = self.assertResponse(create_tournament(user1, private=True), 201, get_field='code')
        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(invite_user(user2, user3, code), 403, {'detail': 'Only creator can update this tournament.'}) # pas bon message d'erreur
        self.assertThread(user1, user2, user3)

    def test_007_user_already_in_tournament(self):
        user1 = self.user(['tournament-join'])
        user2 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')
        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(invite_user(user1, user2, code), 409, {'detail': 'This user is already in this tournament.'})
        self.assertThread(user1, user2)

    def test_008_not_in_tournament(self):
        user1 = self.user()
        user2 = self.user()
        user3 = self.user()

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')
        self.assertResponse(invite_user(user2, user3, code), 403, {'detail': 'You do not belong to this tournament.'})
        self.assertThread(user1, user2, user3)


class Test09_StartTournament(UnitTest):

    def test_001_start_tournament_full(self):
        user1 = self.user(['tournament-join'] * 3 + ['tournament-start'])
        user2 = self.user(['tournament-join'] * 2 + ['tournament-start'])
        user3 = self.user(['tournament-join'] + ['tournament-start'])
        user4 = self.user(['tournament-start'])

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')
        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(join_tournament(user3, code), 201)
        self.assertResponse(join_tournament(user4, code), 201)

        self.assertResponse(create_tournament(user1, method='GET'), 200)
        self.assertThread(user1, user2, user3, user4)

    def test_002_start_tournament_80(self):
        users = [self.user(['tournament-join'] * (5 - i) + ['tournament-start-at', 'tournament-join', 'tournament-join', 'tournament-start', 'game-start']) for i in range(6)]
        user1 = self.user(['tournament-join', 'tournament-start', 'game-start'])
        user2 = self.user(['tournament-start', 'game-start'])

        code = self.assertResponse(create_tournament(users[0], size=8), 201, get_field='code')
        for u in users[1:]:
            self.assertResponse(join_tournament(u, code), 201)

        time.sleep(5)
        self.assertResponse(join_tournament(user1, code), 201)
        self.assertResponse(join_tournament(user2, code), 201)
        time.sleep(10)
        self.assertThread(user1, user2, *users)

    def test_003_cancel_start(self):
        user1 = self.user(['tournament-join', 'tournament-join', 'tournament-join', 'tournament-join', 'tournament-join', 'tournament-join', 'tournament-join', 'tournament-start-at', 'tournament-leave', 'tournament-start-cancel'])
        user2 = self.user(['tournament-join', 'tournament-join', 'tournament-join', 'tournament-join', 'tournament-join', 'tournament-join', 'tournament-start-at', 'tournament-leave', 'tournament-start-cancel'])
        user3 = self.user(['tournament-join', 'tournament-join', 'tournament-join', 'tournament-join', 'tournament-join', 'tournament-start-at', 'tournament-leave', 'tournament-start-cancel'])
        user4 = self.user(['tournament-join', 'tournament-join', 'tournament-join', 'tournament-join', 'tournament-start-at', 'tournament-leave', 'tournament-start-cancel'])
        user5 = self.user(['tournament-join', 'tournament-join', 'tournament-join', 'tournament-start-at', 'tournament-leave', 'tournament-start-cancel'])
        user6 = self.user(['tournament-join', 'tournament-join', 'tournament-start-at', 'tournament-leave', 'tournament-start-cancel'])
        user7 = self.user(['tournament-join', 'tournament-start-at', 'tournament-leave', 'tournament-start-cancel'])
        user8 = self.user(['tournament-start-at'])

        code = self.assertResponse(create_tournament(user1, size=10), 201, get_field='code')
        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(join_tournament(user3, code), 201)
        self.assertResponse(join_tournament(user4, code), 201)
        self.assertResponse(join_tournament(user5, code), 201)
        self.assertResponse(join_tournament(user6, code), 201)
        self.assertResponse(join_tournament(user7, code), 201)
        self.assertResponse(join_tournament(user8, code), 201)

        time.sleep(2)
        self.assertResponse(join_tournament(user8, code, method='DELETE'), 204)
        time.sleep(2)

        self.assertThread(user1, user2, user3, user4, user5, user6, user7, user8)


class Test10_FinishTournament(UnitTest):

    def test_001_finish(self):
        user1 = self.user(['tournament-join', 'tournament-join', 'tournament-join', 'tournament-start', 'game-start', 'tournament-match-finish', 'tournament-match-finish', 'game-start', 'tournament-match-finish', 'tournament-finish'])
        user2 = self.user(['tournament-join', 'tournament-join', 'tournament-start', 'game-start', 'tournament-match-finish', 'tournament-match-finish'])
        user3 = self.user(['tournament-join', 'tournament-start', 'game-start', 'tournament-match-finish', 'tournament-match-finish'])
        user4 = self.user(['tournament-start', 'game-start', 'tournament-match-finish', 'tournament-match-finish', 'tournament-match-finish', 'tournament-finish'])

        code = self.assertResponse(create_tournament(user1), 201, get_field='code')
        self.assertResponse(join_tournament(user2, code), 201)
        self.assertResponse(join_tournament(user3, code), 201)
        self.assertResponse(join_tournament(user4, code), 201)

        time.sleep(5)

        self.assertResponse(score(user1['id']), 204)
        self.assertResponse(score(user1['id']), 204)
        self.assertResponse(score(user1['id']), 204)

        response = score(user2['id'])
        if response.status_code == 204:
            user2['thread_tests'] += ['game-start', 'tournament-match-finish', 'tournament-finish']
            user3['thread_tests'] += ['tournament-match-finish', 'tournament-finish']
            self.assertResponse(response, 204)
            self.assertResponse(score(user2['id']), 204)
            self.assertResponse(score(user2['id']), 204)
        else:
            user3['thread_tests'] += ['game-start', 'tournament-match-finish', 'tournament-finish']
            user2['thread_tests'] += ['tournament-match-finish', 'tournament-finish']
            self.assertResponse(score(user3['id']), 204)
            self.assertResponse(score(user3['id']), 204)
            self.assertResponse(score(user3['id']), 204)
        user2['expected_thread_result'] = len(user2['thread_tests'])
        user3['expected_thread_result'] = len(user3['thread_tests'])

        time.sleep(5)

        self.assertResponse(score(user1['id']), 204)
        self.assertResponse(score(user1['id']), 204)
        self.assertResponse(score(user1['id']), 204)

        self.assertThread(user1, user2, user3, user4)


if __name__ == '__main__':
    unittest.main()
