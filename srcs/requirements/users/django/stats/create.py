from lib_transcendence.game import GameMode


def create_user_stats(user):
    for game_mode in [GameMode.GLOBAL] + GameMode.attr():
        if game_mode == GameMode.CUSTOM_GAME:
            continue
        kwargs = {'game_mode': game_mode}
        if GameMode.tournament_field(game_mode):
            kwargs['tournament_wins'] = 0
        if GameMode.own_goal_field(game_mode):
            kwargs['own_goals'] = 0
        user.stats.create(**kwargs)
    user.ranked_stats.create(trophies=0, total_trophies=0)
