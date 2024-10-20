

class GameMode:
    duel = 'duel'
    clash = 'clash'
    ranked = 'ranked'
    tounament = 'tournament'
    custom_game = 'custom_game'

    @staticmethod
    def all():
        return [GameMode.duel, GameMode.clash, GameMode.ranked, GameMode.tounament, GameMode.custom_game]

    def __str__(self):
        return "'" + ", '".join(GameMode.all()[:-1]) + "' or '" + GameMode.all()[-1]
