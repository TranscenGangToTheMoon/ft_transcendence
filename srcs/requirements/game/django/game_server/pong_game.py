from datetime import datetime, timezone
from game_server.match import Match, Player
# from game_server.pong_ball import Ball
from game_server.pong_position import Position
from game_server.pong_racket import Racket
from typing import List
import os
import time


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
        self.game_timeout = None
        if self.match.game_mode == 'ranked':
            self.game_timeout = 5
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
            racket = Racket(player.user_id, Position(0, int(self.canvas.y / 2 - racket_size.y / 2)), racket_size.x, racket_size.y)
            player.racket = racket
            self.rackets.append(racket)
        # create rackets for right players
        for player in self.match.teams[1].players:
            racket = Racket(player.user_id, Position(self.canvas.x - racket_size.x, int(self.canvas.y / 2 - racket_size.y / 2)), racket_size.x, racket_size.y)
            player.racket = racket
            self.rackets.append(racket)

    def get_racket(self, player_id) -> Racket:
        for racket in self.rackets:
            if racket.player_id == player_id:
                return racket
        raise Exception(f'no racket matching socket id {player_id}')

    def update(self):
        for racket in self.rackets:
            racket.update()
        # self.ball.update()

    def get_player(self, user_id: int) -> Player:
        for team in self.match.teams:
            for player in team.players:
                if player.user_id == user_id:
                    return player
        raise Exception(f'cannot find player with user_id {user_id}')

    def wait_for_players(self, timeout: int):
        start_waiting = time.time()
        for team in self.match.teams:
            for player in team.players:
                while player.socket_id == '':
                    if time.time() - start_waiting > timeout:
                        raise Exception(f'player socketio connection timed out : player_id: {player.user_id}')
                    time.sleep(1)
                #print(f'player {player.user_id} has join in!', flush=True)

    def play(self):
        start_time = time.time()
        last_frame_time = time.time()
        while True:
            if self.game_timeout is not None and (time.time() - start_time < self.game_timeout * 60):
                break
            while time.time() - last_frame_time >= (1 / 60):
                time.sleep(0.005)
            self.update()
            last_frame_time = time.time()

    def launch(self):
        # try:
        #     timeout = int(os.environ['GAME_PLAYER_CONNECT_TIMEOUT'])
        # except KeyError:
        timeout = 60
        try:
            self.wait_for_players(timeout)
        except Exception as e:
            #print(e, flush=True)
            self.match.model.finish_match()
            return
        #print('game launched', flush=True)
        self.play()

    def check_zombie(self) -> bool:
        if self.match.model.finished:
            return True
        game_start_time: datetime = self.match.model.created_at
        game_timeout = self.match.model.game_duration
        now = datetime.now(timezone.utc)
        if game_start_time <= now - game_timeout:
            self.match.model.finish_match()
            return True
        return False
