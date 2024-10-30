from utils import validate_type


class Teams:
    a = 'Team A'
    b = 'Team B'
    spectator = 'Spectator'

    play = [a, b]
    all = play + [spectator]

    @staticmethod
    def validate(value):
        return validate_type(value, Teams, Teams.all)

    def __str__(self):
        return 'Match type'


class MatchType:
    m1v1 = '1v1'
    m3v3 = '3v3'

    @staticmethod
    def validate(value):
        return validate_type(value, MatchType, [MatchType.m1v1, MatchType.m3v3])

    def __str__(self):
        return 'Match type'
