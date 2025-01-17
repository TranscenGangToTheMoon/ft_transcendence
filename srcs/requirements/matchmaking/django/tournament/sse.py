from lib_transcendence.sse_events import EventCode, create_sse_event


def send_sse_event_finish_match(tournament, winner_user_id, looser, score_winner, score_looser, finish_reason):
    from tournament.serializers import TournamentSerializer

    create_sse_event(tournament.users_id(), EventCode.TOURNAMENT_MATCH_FINISH, TournamentSerializer(tournament).data, {'winner': winner_user_id, 'looser': looser, 'score_winner': score_winner, 'score_looser': score_looser, 'finish_reason': finish_reason})
