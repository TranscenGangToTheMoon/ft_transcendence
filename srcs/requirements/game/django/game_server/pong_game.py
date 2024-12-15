from datetime import datetime, timezone
import math
from game_server.match import Match, Player
from game_server.pong_ball import Ball
from game_server.pong_position import Position
from game_server.pong_racket import Racket
from typing import List
import asyncio
import os
import time
import random


def get_random_direction():
    random_angle = random.random() * 2 * math.pi
    while abs(math.cos(random_angle)) < math.cos(math.pi / 3):
        print(random_angle, abs(math.cos(random_angle)), flush=True)
        random_angle = random.random() * 2 * math.pi
    return math.cos(random_angle), math.sin(random_angle)


class Game:
    @staticmethod
    def create_ball(canvas: Position):
        direction_x, direction_y = get_random_direction()
        ball_speed = 2
        ball_size = 20
        return Ball(Position(int(canvas.x / 2), int(canvas.y / 2)), direction_x, direction_y, ball_speed, ball_size)

    @staticmethod
    def create_rackets(match, canvas) -> List[Racket]:
        rackets: List[Racket] = []
        racket_size: Position = Position(30, 200)
        # create rackets for left players
        for player in match.teams[0].players:
            racket = Racket(player.user_id, Position(0, int(canvas.y / 2 - racket_size.y / 2)), racket_size.x, racket_size.y)
            player.racket = racket
            rackets.append(racket)
        # create rackets for right players
        for player in match.teams[1].players:
            racket = Racket(player.user_id, Position(canvas.x - racket_size.x, int(canvas.y / 2 - racket_size.y / 2)), racket_size.x, racket_size.y)
            player.racket = racket
            rackets.append(racket)
        return rackets

    def __init__(self,
                sio,
                match,
                canvas: Position = Position(0, 0)) -> None:
        self.match: Match = match
        self.sio = sio
        self.canvas = canvas
        self.game_timeout = None
        if self.match.game_mode == 'ranked':
            self.game_timeout = 5
        if self.canvas == Position(0, 0):
            try:
                self.canvas = Position(
                    int(os.environ['CANVAS_SIZE_X']),
                    int(os.environ['CANVAS_SIZE_X'])
                )
            except KeyError:
                self.canvas = Position(800, 600)

        self.max_bounce_angle = 2 * (math.pi / 5)
        self.max_ball_speed = 15
        self.ball = self.create_ball(self.canvas)
        self.rackets = self.create_rackets(self.match, self.canvas)

    def get_racket(self, player_id) -> Racket:
        for racket in self.rackets:
            if racket.player_id == player_id:
                return racket
        raise Exception(f'no racket matching socket id {player_id}')



    # def calculate_impact_position(self, ball_y, paddle_y, paddle_height):
    #     relative_y = (paddle_y + paddle_height / 2) - ball_y
    #     return relative_y / (paddle_height / 2)

    # def calculate_new_ball_direction(self, paddle_y, paddle_direction=0):
    #     # Calculer la position d'impact
    #     impact_position = self.calculate_impact_position(
    #         self.ball.y + self.config.ball_size / 2,
    #         paddle_y,
    #         self.config.paddle_height
    #     )
    #     print(impact_position)

    #     # Calculer l'angle de rebond
    #     # bounce_angle = impact_position * self.config.max_bounce_angle

    #     # Ajouter une logique d'influence de vitesse ici si nécessaire

    #     # Calculer les nouvelles vitesses en fonction de l'angle de rebond
    #     direction = math.acos(self.ball.direction_x)
    #     if (direction != math.asin(self.ball.direction_y)):
    #         direction = -direction
    #     x_new_direction = direction * math.cos(bounce_angle)
    #     y_new_direction = direction * -math.sin(bounce_angle)

    #     print(x_new_direction, y_new_direction)

    #     # Mise à jour des vitesses de la balle
    #     self.ball.direction_x = x_new_direction * -1 if self.ball.direction_x < 0 else x_new_direction
    #     self.ball.direction_y = y_new_direction

    #     print(self.ball.direction_x, self.ball.direction_y)


    # def handle_racket_collision(self):
    #     for paddle in self.rackets:
    #         if paddle.block_glide:
    #             self.ball.direction_y = -self.ball.direction_y
    #             if abs(self.ball.position.y - (paddle.position.y + paddle.height)) < abs(self.ball.position.y - paddle.position.y):
    #                 self.ball.position.y = paddle.position.y + paddle.height
    #             else:
    #                 self.ball.position.y = paddle.position.y - self.ball.size
    #         else:
    #             self.ball.direction_x = -self.ball.direction_x
    #             # if self.ball.speed < self.max_ball_speed:
    #             #     self.increment_ball_speed()
    #             self.calculate_new_ball_direction(paddle.position.y)
    #             self.sio.emit('bounce', {'dir_x': self.ball.direction_x, 'dir_y': self.ball.direction_y})


    def update(self):
        for racket in self.rackets:
            racket.update()
        # update ball position
        self.ball.position.x += self.ball.direction_x * self.ball.speed
        self.ball.position.x += self.ball.direction_y * self.ball.speed
        # update ball direction (in case it bounces)

    def get_player(self, user_id: int) -> Player:
        for team in self.match.teams:
            for player in team.players:
                if player.user_id == user_id:
                    return player
        raise Exception(f'cannot find player with user_id {user_id}')

    def wait_for_players(self, timeout: float):
        print(time.time(), "wait_for_players()", flush=True)
        start_waiting = time.time()
        for team in self.match.teams:
            for player in team.players:
                while player.socket_id == '':
                    if time.time() - start_waiting > timeout:
                        raise Exception(f'player socketio connection timed out : player_id: {player.user_id}')
                    time.sleep(0.1)
                print(time.time(),flush=True)
                print(f'player {player.user_id} has join in!', flush=True)

    async def play(self):
        start_time = time.time()
        last_frame_time = start_time
        side = 1
        print(time.time(), "emitting start_game", flush=True)
        await self.sio.emit('debug')
        for team in self.match.teams:
            for player in team.players:
                await self.sio.emit(
                    'start_game',
                    data={
                        'position_x': self.ball.position.x,
                        'position_y': self.ball.position.y,
                        'direction_x': self.ball.direction_x * side,
                        'direction_y': self.ball.direction_y,
                        'canvas_width': self.canvas.x,
                        'canvas_height': self.canvas.y
                    },
                    to=player.socket_id
                )
            side = -1
        print(time.time(), "Finished emitting start_game", flush=True)
        while True:
            print(time.time(), "game loop", flush=True)
            if self.game_timeout is not None and (time.time() - start_time < self.game_timeout * 60):
                break
            while time.time() - last_frame_time < (1 / 60):
                time.sleep(0.005)
            self.update()
            last_frame_time = time.time()

    async def launch(self):
        # try:
        #     timeout = int(os.environ['GAME_PLAYER_CONNECT_TIMEOUT'])
        # except KeyError:
        print(time.time(), "launch()", flush=True)
        timeout = 60.
        try:
            self.wait_for_players(timeout)
            print(time.time(), "wait_for_players() ended", flush=True)
        except Exception as e:
            print(time.time(), "wait_for_players() ended", flush=True)
            #print(e, flush=True)
            self.match.model.finish_match()
            return
        print('game launched', flush=True)
        await self.play()

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

    async def score(self):
        self.ball.position = Position(int(self.canvas.x / 2), int(self.canvas.y / 2))
        self.ball.direction_x, self.ball.direction_y = get_random_direction()
        side = 1
        for team in self.match.teams:
            for player in team.players:
                await self.sio.emit(
                    'goal',
                    data={
                        'position_x': self.ball.position.x,
                        'position_y': self.ball.position.y,
                        'direction_x': self.ball.direction_x * side,
                        'direction_y': self.ball.direction_y
                    },
                    to=player.socket_id
                )
            side = -1
