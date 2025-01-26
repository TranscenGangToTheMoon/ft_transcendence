EXT = '.png'


class ProfilePictures:
    DEFAULT = 'Default'
    TOURNAMENT_WINNER = 'Tournament Winner'
    TOURNAMENT_MASTER = 'Tournament Master'
    TOURNAMENT_GOD = 'Tournament God'
    CLASH_WINNER = 'Clash Winner'
    CLASH_PLAYER = 'Clash Player'
    CLASH_GOD = 'Clash God'
    DUEL_WINNER = 'Duel Winner'
    DUEL_MASTER = 'Duel Master'
    DUEL_GOD = 'Duel God'
    RANKE_BRONZE = 'Ranke Bronze'
    RANKE_SILVER = 'Ranke Silver'
    RANKE_GOLD = 'Ranke Gold'
    RANKE_DIAMOND = 'Ranke Diamond'
    RANKE_MASTER = 'Ranke Master'
    RANKE_MYTHIC = 'Ranke Mythic'
    FUN_PLAYER = 'Fun Player'
    SCORER = 'Scorer'
    ONE_FRIEND = 'One Friend'
    POPULAR_GUY = 'Popular Guy'

    def __init__(self, name, unlock_reason):
        self.name = name
        self.unlock_reason = unlock_reason
        url = '/assets/profile_pictures/' + name.lower().replace(' ', '_')
        self.url = url + EXT
        self.small = url + '_small' + EXT
        self.medium = url + '_medium' + EXT
        self.large = url + '_large' + EXT

    def __dict__(self):
        return {
            'name': self.name,
            'unlock_reason': self.unlock_reason,
            'url': self.url,
            'small': self.small,
            'medium': self.medium,
            'large': self.large,
        }


profile_pictures = [
    ProfilePictures(ProfilePictures.DEFAULT, 'Default profile picture'),
    ProfilePictures(ProfilePictures.TOURNAMENT_WINNER, 'Win 1 tournament'),
    ProfilePictures(ProfilePictures.TOURNAMENT_MASTER, 'Win 10 tournaments'),
    ProfilePictures(ProfilePictures.TOURNAMENT_GOD, 'Win 100 tournaments'),
    ProfilePictures(ProfilePictures.CLASH_WINNER, 'Win 10 clash games.'),
    ProfilePictures(ProfilePictures.CLASH_PLAYER, 'Win 50 clash games.'),
    ProfilePictures(ProfilePictures.CLASH_GOD, 'Win 100 clash games.'),
    ProfilePictures(ProfilePictures.DUEL_WINNER, 'Win 10 duel games.'),
    ProfilePictures(ProfilePictures.DUEL_MASTER, 'Win 50 duel games.'),
    ProfilePictures(ProfilePictures.DUEL_GOD, 'Win 100 duel games.'),
    ProfilePictures(ProfilePictures.RANKE_BRONZE, 'Achieve over 100 trophies in ranked'),
    ProfilePictures(ProfilePictures.RANKE_SILVER, 'Achieve over 500 trophies in ranked'),
    ProfilePictures(ProfilePictures.RANKE_GOLD, 'Achieve over 1000 trophies in ranked'),
    ProfilePictures(ProfilePictures.RANKE_DIAMOND, 'Achieve over 2000 trophies in ranked'),
    ProfilePictures(ProfilePictures.RANKE_MASTER, 'Achieve over 3000 trophies in ranked'),
    ProfilePictures(ProfilePictures.RANKE_MYTHIC, 'Achieve over 5000 trophies in ranked'),
    ProfilePictures(ProfilePictures.FUN_PLAYER, 'Play a match in all game modes'),
    ProfilePictures(ProfilePictures.SCORER, 'Score 100 goals in any game mode'),
    ProfilePictures(ProfilePictures.ONE_FRIEND, 'Have at least one friend'),
    ProfilePictures(ProfilePictures.POPULAR_GUY, 'Have more than 50 friends'),
]
