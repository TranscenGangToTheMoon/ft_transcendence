from lib_transcendence.validate_type import validate_type, surchage_list


class TournamentSize:
    S4 = 4
    S8 = 8
    S16 = 16

    @staticmethod
    def validate(mode):
        return validate_type(mode, TournamentSize)

    @staticmethod
    def attr():
        return surchage_list(TournamentSize)

    def __str__(self):
        return 'Tournament size'
