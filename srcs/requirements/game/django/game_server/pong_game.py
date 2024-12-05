from typing import List
# from game_server.pong_ball import Ball
from game_server.pong_racket import Racket
from game_server.pong_position import Position
from game_server.match import Match, Player
import time
import os

def get_random_direction() -> Position:
    return Position(0, 0)

class Game:
    def __init__(self,
                sio,
                match,
                canvas: Position | None = None) -> None:
        self.match: Match = match
        self.sio = sio
        self.canvas = canvas
        if self.canvas is None:
            try:
                self.canvas = Position(
                    int(os.environ['CANVAS_SIZE_X']),
                    int(os.environ['CANVAS_SIZE_X'])
                )
            except KeyError:
                self.canvas = Position(800, 600)

        # direction = get_random_direction()
        # self.ball = Ball(Position(int(canvas_size.x / 2), int(canvas_size.y / 2)), direction)

        racket_size: Position = Position(10, 100)
        self.rackets: List[Racket] = []
        # create rackets for left players
        for player in self.match.teams[0].players:
            self.rackets.append(Racket(player.user_id, Position(0, int(self.canvas.y / 2 - racket_size.y / 2)), racket_size.x, racket_size.y))
        # create rackets for right players
        for player in self.match.teams[1].players:
            self.rackets.append(Racket(player.user_id, Position(self.canvas.x - racket_size.x, int(self.canvas.y / 2 - racket_size.y / 2)), racket_size.x, racket_size.y))


    def get_racket(self, player_id) -> Racket:
        for racket in self.rackets:
            if racket.player_id == player_id:
                return racket
        raise Exception(f'no racket matching socket id {player_id}')

    def update(self):
        pass

    def get_player(self, user_id: int) -> Player:
        for team in self.match.teams:
            for player in team.players:
                if player.user_id == user_id:
                    return player
        raise Exception(f'cannot find player with user_id {user_id}')

    def wait_for_players(self, timeout: int):
        start_waiting = time.time()
        # for team in self.match.teams:
        print(self.match.teams[0].model, flush=True)
        # for player in self.match.teams[0].players:
        while self.match.teams[0].players[0].socket_id == '':
            if time.time() - start_waiting > timeout:
                raise Exception(f'player socketio connection timed out : player_id: {self.match.teams[0].players[0].user_id}')
            time.sleep(1)
        print(f'player {self.match.teams[0].players[0].user_id} has join in!', flush=True)

    def launch(self):
        # try:
        #     timeout = int(os.environ['GAME_PLAYER_CONNECT_TIMEOUT'])
        # except KeyError:
        timeout = 60
        try:
            self.wait_for_players(timeout)
        except Exception as e:
            print(e, flush=True)
            self.match.model.finished = True
            self.match.model.save()
            return
        print('game launched', flush=True)
        start_time = time.time()
        while (time.time() - start_time < 120):
            time.sleep(0.02)
            print(self.rackets[0].velocity, flush=True)
