from aiohttp.web_routedef import AbstractRouteDef
from typing import List
from lib_transcendence.request import AuthenticationFailed
from lib_transcendence.services import request_game
from lib_transcendence.game import FinishReason
from lib_transcendence import endpoints
from rest_framework.exceptions import APIException, NotFound
from game_server.pong_racket import Racket


class Player():
    def __init__(self, id, match_id, team):
        self.match_id = match_id
        self.racket: Racket
        self.user_id = id
        self.socket_id = ''
        self.game = None
        self.team = team
        self.score = 0
        self.csc = 0

    def score_goal(self, csc=False):
        try:
            instance = request_game(endpoints.Game.fscore.format(user_id=self.user_id), 'PUT', data={'own_goal': csc})
        except NotFound as e:
            print(e.detail, flush=True)
            return None
        except APIException as e:
            return None
        if csc:
            self.csc += 1
        else:
            self.score += 1
        return instance

    def __str__(self) -> str:
        return str(self.user_id)


class Team():
    def __init__(self, players, match_id, name):
        self.match_id = match_id
        self.players: List[Player] = []
        self.name = name
        self.score = 0
        for player in players:
            self.players.append(Player(player['id'], match_id, self))

    def __str__(self) -> str:
        return self.name + ': ' + ', '.join([str(player) for player in self.players]) + 'score: ' + str(self.score)


class Match():
    def __init__(self, game_data):
        self.id = game_data['id']
        self.teams: List[Team] = []
        self.game_mode = game_data['game_mode']
        teams = game_data['teams']
        for team_name, team in teams.items():
            self.teams.append(Team(team['players'], self.id, team_name))
        self.game_type = 'clash' if len(self.teams[0].players) == 3 else 'normal'


def finish_match(match_id, finish_reason: str, user_id: int):
    if finish_reason != FinishReason.NORMAL_END:
        try:
            print('sending finish request')
            request_game(
                endpoints.Game.ffinish_match.format(match_id=match_id),
                'PUT',
                data={
                    'finish_reason': finish_reason,
                    'user_id': user_id
                }
            )
        except AuthenticationFailed as e:
            print("The finish_match attribute is not available in the Game class.", flush=True)
        except Exception as e:
            print(f"An error occurred while requesting the game finish: {e}", flush=True)
