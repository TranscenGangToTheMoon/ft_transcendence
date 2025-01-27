from lib_transcendence.game import GameMode
from profile_pictures.data import ProfilePicture
from profile_pictures.models import ProfilePictures


def unlock_tournament_pp(user):
    for pp_name, required_wins in ((ProfilePicture.TOURNAMENT_WINNER, 1), (ProfilePicture.TOURNAMENT_MASTER, 10), (ProfilePicture.TOURNAMENT_GOD, 100)):
        try:
            assert user.stats.get(game_mode=GameMode.TOURNAMENT).tournament_wins >= required_wins
            pp = user.profile_pictures.get(name=pp_name, is_unlocked=False)
            pp.unlock()
        except (AssertionError, ProfilePictures.DoesNotExist):
            pass


def unlock_duel_clash_pp(user, stat, game_mode):
    for pp_name, required_wins in (('WINNER', 10), ('MASTER', 50), ('GOD', 100)):
        try:
            assert stat.wins >= required_wins
            pp = user.profile_pictures.get(name=getattr(ProfilePicture, f'{game_mode.upper()}_{pp_name}'), is_unlocked=False)
            pp.unlock()
        except (AssertionError, ProfilePictures.DoesNotExist):
            pass


def unlock_ranked_pp(user, trophies):
    for pp_name, required_trophies in (('BRONZE', 100), ('SILVER', 500), ('GOLD', 1000), ('DIAMOND', 2000), ('MASTER', 3000), ('MYTHIC', 5000)):
        try:
            assert trophies >= required_trophies
            pp = user.profile_pictures.get(name=getattr(ProfilePicture, f'RANKED_{pp_name}'), is_unlocked=False)
            pp.unlock()
        except (AssertionError, ProfilePictures.DoesNotExist):
            pass


def unlock_game_played_pp(user):
    try:
        assert 5 == user.stats.filter(wins__gte=1).count()
        pp = user.profile_pictures.get(name=ProfilePicture.FUN_PLAYER, is_unlocked=False)
        pp.unlock()
    except (AssertionError, ProfilePictures.DoesNotExist):
        pass


def unlock_score_pp(user):
    for pp_name, required_score in ((ProfilePicture.SCORER, 100), (ProfilePicture.GOD_SCORER, 1000)):
        try:
            assert user.stats.get(game_mode=GameMode.GLOBAL).scored >= required_score
            pp = user.profile_pictures.get(name=pp_name, is_unlocked=False)
            pp.unlock()
        except (AssertionError, ProfilePictures.DoesNotExist):
            pass


def unlock_winning_streak_pp(user, stat):
    try:
        assert stat.longest_win_streak >= 10
        pp = user.profile_pictures.get(name=ProfilePicture.WIN_STREAK_PLAYER, is_unlocked=False)
        pp.unlock()
    except (AssertionError, ProfilePictures.DoesNotExist):
        pass


def unlock_friends_pp(friend_instance):
    for user in (friend_instance.user_1, friend_instance.user_2):
        for pp_name, required_friends in ((ProfilePicture.ONE_FRIEND, 1), (ProfilePicture.POPULAR_GUY, 50)):
            try:
                assert (user.friend_1.count() + user.friend_2.count()) >= required_friends
                pp = user.profile_pictures.get(name=pp_name, is_unlocked=False)
                print(pp, pp.name, pp.n, flush=True)
                pp.unlock()
            except (AssertionError, ProfilePictures.DoesNotExist):
                pass
