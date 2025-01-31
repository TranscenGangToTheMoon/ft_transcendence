import time
from datetime import datetime, timezone

from django.db import models

from lib_transcendence import endpoints
from lib_transcendence.services import request_users
from lib_transcendence.sse_events import EventCode, create_sse_event


# todo handle tournament message

class Tournaments(models.Model):
    stage_labels = {0: 'final', 1: 'semi-final', 2: 'quarter-final', 3: 'round-of-16'}
    match_order = {
        4: {1: 1, 2: 2},
        8: {1: 1, 2: 3, 3: 4, 4: 2},
        16: {1: 1, 2: 5, 3: 7, 4: 3, 5: 4, 6: 8, 7: 6, 8: 2},
    }

    name = models.CharField(max_length=50, unique=True)
    size = models.IntegerField(default=16)
    nb_matches = models.IntegerField(default=1)
    current_stage = models.ForeignKey('TournamentStage', on_delete=models.SET_NULL, default=None, null=True, related_name='current_stage')
    start_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField()
    created_by_username = models.CharField(max_length=30)
    update_stage = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    finish_at = models.DateTimeField(default=None, null=True)

    def finish(self):
        self.finished = True
        self.finish_at = datetime.now(timezone.utc)
        self.save()
        winner_user_id = self.players.filter(still_in=True).first().user_id
        self.players.all().update(still_in=False)
        create_sse_event(self.users_id(), EventCode.TOURNAMENT_FINISH, {'id': self.id}, {'name': self.name, 'username': winner_user_id})
        request_users(endpoints.Users.result_tournament, method='POST', data={'winner': winner_user_id})

    def main_thread(self):
        time.sleep(5)
        while True:
            time.sleep(3)
            if self.current_stage.stage == 0:
                self.finish()
                return
            matches = self.current_stage.matches.all()
            if matches.filter(finished=False).exists():
                continue

            time.sleep(1)
            stage = self.stages.get(stage=self.current_stage.stage - 1)

            spectate = {}
            previous = None
            for match in matches.order_by('tournament_n'):
                if previous is None:
                    previous = match
                    continue
                self.create_match(self.get_nb_matches(), stage, previous.winner.players.first(), match.winner.players.first())
                spectate[match.id] = match.code
                previous = None

            self.current_stage = stage
            self.save()
            self.post_matches(stage)
            create_sse_event(self.users_id(), EventCode.TOURNAMENT_AVAILABLE_SPECTATE_MATCHES, spectate)

    def get_nb_matches(self):
        self.nb_matches += 1
        self.save()
        return self.nb_matches

    def set_update_stage(self, value: bool):
        self.update_stage = value
        self.save()

    def users_id(self):
        return list(self.players.values_list('user_id', flat=True))

    def post_matches(self):
        time.sleep(3)
        for matche in self.matches.filter(tournament_stage=self.current_stage):
            matche.post()


class TournamentStage(models.Model):
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, related_name='stages')
    label = models.CharField(max_length=50)
    stage = models.IntegerField()


class TournamentPlayers(models.Model):
    user_id = models.IntegerField()
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, related_name='players')
    stage = models.ForeignKey(TournamentStage, on_delete=models.CASCADE, default=None, null=True, related_name='players')
    seed = models.IntegerField(default=None, null=True)
    trophies = models.IntegerField()
    index = models.IntegerField(default=None, null=True)
    still_in = models.BooleanField(default=True)
    creator = models.BooleanField(default=False)
    join_at = models.DateTimeField(auto_now_add=True)

    @property
    def place(self):
        return self.tournament

    def eliminate(self):
        self.still_in = False
        self.save()

    def win(self):
        cur = self.stage.stage
        if cur == 0:
            return True
        self.stage = self.tournament.stages.get(stage=cur - 1)
        self.save()
        return False


    # def post(self):
    #     if self.user_2 is not None:
    #         if not self.user_1.still_in:
    #             create_tournament_match_not_played(self.tournament.id, self.stage.id, self.n, self.user_2)
    #             self.finish(self.user_2)
    #         else:
    #             try:
    #                 match = create_tournament_match(self.tournament.id, self.stage.id, self.n, self.user_1.user_id, self.user_2.user_id)
    #                 self.match_id = match['id']
    #                 self.match_code = match['code']
    #                 self.save()
    #             except APIException:
    #                 self.finish(None)
    #     elif self.user_1 is not None and self.user_1.still_in:
    #         create_tournament_match_not_played(self.tournament.id, self.stage.id, self.n, self.user_1)
    #         self.finish(self.user_1)
    #     else:
    #         self.finish(None)
    #
    # def finish(self, winner, looser=None, validated_data=None):
    #     self.finished = True
    #     self.winner = winner
    #     self.match_code = None
    #     self.save()
    #     tournament = self.tournament
    #     if validated_data is None:
    #         if winner is None:
    #             validated_data = {'score_winner': 0, 'score_looser': 0, 'finish_reason': FinishReason.NO_GAME}
    #         else:
    #             validated_data = {'score_winner': 3, 'score_looser': 0, 'finish_reason': FinishReason.GAME_NOT_PLAYED}
    #     else:
    #         validated_data.pop('winner_id')
    #     if winner is None:
    #         winner_user_id = None
    #     else:
    #         winner_user_id = winner.user_id
    #     if validated_data['finish_reason'] == FinishReason.NORMAL_END:
    #         finish_reason = ''
    #     elif validated_data['finish_reason'] == FinishReason.PLAYER_DISCONNECT:
    #         finish_reason = ' (obviously the other player gave up the game)'
    #     elif validated_data['finish_reason'] == FinishReason.GAME_NOT_PLAYED:
    #         finish_reason = ' (yeah, there just was no game)'
    #     elif validated_data['finish_reason'] == FinishReason.NO_GAME:
    #         finish_reason = ' (there was no game, so nobody won)'
    #     else:
    #         finish_reason = ' (obviously he played against nobody, not too complicated to win)'
    #     send_sse_event_finish_match(tournament, winner_user_id, 'nobody' if looser is None else looser.user_id, validated_data['score_winner'], validated_data['score_looser'], finish_reason)
    #
    #     if winner is None and self.stage.stage == 0:
    #         self.tournament.delete()
    #         return
    #
    #     if winner is not None:
    #         finished = winner.win()
    #     else:
    #         finished = False
    #
    #     if looser is not None:
    #         looser.eliminate()
    #
    #     if finished:
    #         from tournament.utils import finish_tournament
    #
    #         finish_tournament(self.tournament.id, winner_user_id)
    #     else:
    #         from tournament.utils import create_match_new_stage
    #
    #         Thread(target=create_match_new_stage, args=(self.tournament.id, )).start()
