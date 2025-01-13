def get_trophies(user):
    return user.ranked_stats.order_by('-at').first().total_trophies
