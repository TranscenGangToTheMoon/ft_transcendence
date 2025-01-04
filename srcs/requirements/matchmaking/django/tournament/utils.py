from lib_transcendence.validate_type import validate_type


class TournamentSize:
    size4 = 4
    size8 = 8
    size16 = 16

    sizes = [size4, size8, size16]

    @staticmethod
    def validate(mode):
        return validate_type(mode, TournamentSize(), TournamentSize.sizes)

    def __str__(self):
        return 'Tournament size'
