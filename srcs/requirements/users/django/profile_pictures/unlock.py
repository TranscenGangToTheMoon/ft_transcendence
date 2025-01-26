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


def unlock_duel_clash_pp(user, game_mode):
    for pp_name, required_wins in (('WINNER', 10), ('MASTER', 50), ('GOD', 100)):
        try:
            assert user.stats.get(game_mode=getattr(GameMode, game_mode)).wins >= required_wins
            pp = user.profile_pictures.get(name=getattr(ProfilePicture, f'{game_mode}_{pp_name}'), is_unlocked=False)
            pp.unlock()
        except (AssertionError, ProfilePictures.DoesNotExist):
            pass


def unlock_ranked_pp(user): # todo remake
    for pp_name, required_wins in (('BRONZE', 100), ('SILVER', 500), ('GOLD', 1000), ('DIAMOND', 2000), ('MASTER', 3000), ('MYTHIC', 5000)):
        try:
            assert user.stats.get(game_mode=GameMode.RANKED).tropgie >= required_wins
            pp = user.profile_pictures.get(name=getattr(ProfilePicture, f'RANKED_{pp_name}'), is_unlocked=False)
            pp.unlock()
        except (AssertionError, ProfilePictures.DoesNotExist):
            pass
