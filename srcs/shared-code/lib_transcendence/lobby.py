from lib_transcendence.validate_type import validate_type, surchage_list


class Teams:
    A = 'Team A'
    B = 'Team B'
    SPECTATOR = 'Spectator'

    @staticmethod
    def validate(value):
        return validate_type(value, Teams)

    @staticmethod
    def attr():
        return surchage_list(Teams)

    def __str__(self):
        return 'Match type'


class MatchType:
    M1V1 = '1v1'
    M3V3 = '3v3'

    @staticmethod
    def validate(value):
        return validate_type(value, MatchType)

    @staticmethod
    def attr():
        return surchage_list(MatchType)

    def __str__(self):
        return 'Match type'
