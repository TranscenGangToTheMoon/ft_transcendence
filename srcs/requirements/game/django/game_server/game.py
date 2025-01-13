from asgiref.sync import async_to_sync
from datetime import datetime, timezone
from game_server.match import Match, Player, finish_match
from game_server.pong_ball import Ball
from game_server.pong_position import Position
from game_server.pong_racket import Racket
from lib_transcendence.game import FinishReason
from typing import List
import asyncio
import math
import os
import random
import requests
import time

def get_random_direction():
    random_angle = random.random() * 2 * math.pi
    while abs(math.cos(random_angle)) < math.cos(math.pi / 3):
        random_angle = random.random() * 2 * math.pi
    return math.cos(random_angle), math.sin(random_angle)


class Game:
    default_ball_speed = 240

    @staticmethod
    def create_ball(canvas: Position):
        direction_x, direction_y = get_random_direction()
        ball_size = 20
        return Ball(Position(int(canvas.x / 2 - (ball_size / 2)), int(canvas.y / 2 - (ball_size / 2))), direction_x, direction_y, Game.default_ball_speed, ball_size)

    @staticmethod
    def create_rackets(match, canvas) -> List[Racket]:
        Racket.width = 30
        Racket.height = 200
        rackets: List[Racket] = []
        racket_size: Position = Position(30, 200)
        # create rackets for right players
        for player in match.teams[0].players:
            racket_offset = 100
            racket = Racket(player.user_id, Position(canvas.x - racket_size.x - racket_offset, int(canvas.y / 2 - racket_size.y / 2)))
            player.racket = racket
            rackets.append(racket)
            racket_offset += 200
        # create rackets for left players
        for player in match.teams[1].players:
            racket_offset = 100
            racket = Racket(player.user_id, Position(racket_offset, int(canvas.y / 2 - racket_size.y / 2)))
            player.racket = racket
            rackets.append(racket)
            racket_offset += 200
        return rackets

    def __init__(self,
                sio,
                match,
                canvas: Position = Position(0, 0)) -> None:
        self.match: Match = match
        self.finished = False
        self.frames = 0
        self.canvas = canvas
        self.game_timeout = None
        if self.match.game_mode == 'ranked':
            self.game_timeout = 5
        if self.canvas == Position(0, 0):
            try:
                self.canvas = Position(
                    int(os.environ['CANVAS_SIZE_X']),
                    int(os.environ['CANVAS_SIZE_Y'])
                )
            except KeyError:
                self.canvas = Position(800, 600)
        # print('canvas', self.canvas.x, self.canvas.y, flush=True)

        # TODO -> set all variables from .env
        self.max_bounce_angle = 2 * (math.pi / 5)
        self.max_ball_speed = 1500
        self.speed_increment = 30
        self.ball = self.create_ball(self.canvas)
        self.rackets = self.create_rackets(self.match, self.canvas)
        self.ball.last_touch_team_a = self.match.teams[0].players[0].user_id
        self.ball.last_touch_team_b = self.match.teams[1].players[0].user_id

    class PlayerTimeout(Exception):
        pass

    class NoSuchPlayer(Exception):
        pass

    class NoSuchRacket(Exception):
        pass


################--------getters--------################

    def get_racket(self, player_id) -> Racket:
        for racket in self.rackets:
            if racket.player_id == player_id:
                return racket
        raise self.NoSuchRacket(f'no racket matching socket id {player_id}')

    def get_player(self, user_id: int) -> Player:
        for team in self.match.teams:
            for player in team.players:
                if player.user_id == user_id:
                    return player
        raise self.NoSuchPlayer(f'cannot find player with user_id {user_id}')

################--------game--------################

    def handle_wall_bounce(self):
        ball_pos_y = self.ball.position.y
        if ball_pos_y <= 0:
            self.ball.position.y = - ball_pos_y
            self.ball.speed_y = - self.ball.speed_y
            print('bouncing up', flush=True)
        elif ball_pos_y + self.ball.size >= self.canvas.y:
            self.ball.position.y -= (ball_pos_y + self.ball.size) - self.canvas.y
            self.ball.speed_y = - self.ball.speed_y
            print('bouncing down', flush=True)

    def handle_goal(self):
        if self.ball.position.x + self.ball.size < 0:
            self.score(self.match.teams[0])
        elif self.ball.position.x > self.canvas.x:
            self.score(self.match.teams[1])

    def calculateImpactPosition(self, ballY, paddleY, paddleHeight):
        relativeY = (paddleY + paddleHeight / 2) - ballY
        return relativeY / (paddleHeight / 2)

    def calculateNewBallDirection(self, paddleY):
        impactPosition = self.calculateImpactPosition(self.ball.position.y + self.ball.size / 2, paddleY, Racket.height)
        bounceAngle = impactPosition * self.max_bounce_angle

        speed = self.ball.speed
        xNewSpeed = speed * math.cos(bounceAngle)
        yNewSpeed = speed * -math.sin(bounceAngle)
        self.ball.speed_x = -xNewSpeed if self.ball.speed_x < 0 else xNewSpeed
        self.ball.speed_y = yNewSpeed

    def handle_racket_bounce(self, racket):
        if (racket.blockGlide):
            self.ball.speed_y = -self.ball.speed_y
            self.ball.direction_y = -self.ball.direction_y
            if (abs(self.ball.position.y - (racket.position.y + racket.height)) <
                abs(self.ball.position.y - (racket.position.y))):
                self.ball.position.y = racket.position.y + racket.height
            else:
                self.ball.position.y = racket.position.y - self.ball.size
        else:
            self.ball.speed_x = -self.ball.speed_x
            self.ball.direction_x = -self.ball.direction_x
            self.ball.increment_speed(self.max_ball_speed, self.speed_increment)
            self.calculateNewBallDirection(racket.position.y)

    @staticmethod
    def is_in_team(player_id, team):
        for team_player in team.players:
            if team_player.user_id == player_id:
                return True
        return False

    def handle_racket_collision(self, racket):
        ball_is_right_from_racket = self.ball.position.x < racket.position.x + racket.width and self.ball.position.x > racket.position.x
        ball_is_left_from_racket = self.ball.position.x + self.ball.size > racket.position.x and self.ball.position.x + self.ball.size < racket.position.x + racket.width
        is_ball_y_in_paddle_range = self.ball.position.y + self.ball.size > racket.position.y and self.ball.position.y < racket.position.y + racket.height

        if (ball_is_left_from_racket == True or ball_is_right_from_racket == True) and is_ball_y_in_paddle_range == True:
            self.handle_racket_bounce(racket)
            self.ball.last_racket_touched = racket.player_id
            if self.is_in_team(racket.player_id, self.match.teams[0]):
                self.ball.last_touch_team_a = racket.player_id
            else:
                self.ball.last_touch_team_b = racket.player_id
            if (not racket.blockGlide):
                if (self.ball.position.x + self.ball.size > racket.position.x and
                    self.ball.position.x + self.ball.size < racket.position.x + racket.width
                ):
                    self.ball.position.x = racket.position.x - self.ball.size;
                else:
                    self.ball.position.x = racket.position.x + racket.width;
        else:
            is_ball_x_in_racket_range = self.ball.position.x < racket.position.x + racket.width and self.ball.position.x + self.ball.size > racket.position.x
            if (is_ball_x_in_racket_range):
                racket.blockGlide = True
            else:
                racket.blockGlide = False

    def update(self):
        if (self.last_update == 0):
            self.last_update = time.perf_counter()
        time_delta = time.perf_counter() - self.last_update
        self.last_update = time.perf_counter()
        for racket in self.rackets:
            racket.update(self.ball.size, self.canvas.y, time_delta)
        self.ball.position.x += self.ball.speed_x * time_delta
        self.ball.position.y += self.ball.speed_y * time_delta
        self.handle_wall_bounce()
        for racket in self.rackets:
            self.handle_racket_collision(racket)
        self.send_game_state()
        self.handle_goal()

    def wait_for_players(self, timeout: float):
        print("waiting for players", flush=True)
        start_waiting = time.time()
        for team in self.match.teams:
            for player in team.players:
                while player.socket_id == '':
                    if time.time() - start_waiting > timeout:
                        raise self.PlayerTimeout('player socketio connection timed out')
                    time.sleep(0.1)
                print(time.time(),flush=True)
                print(f'player {player.user_id} has join in!', flush=True)

    def play(self):
        start_time = time.perf_counter()
        self.send_start_countdown()
        effective_start_time = start_time + 2
        last_frame_time = start_time
        self.last_update = 0
        while time.perf_counter() < effective_start_time:
            time.sleep(1 / 120)
        self.send_start_game()
        while not self.finished:
            if self.game_timeout is not None and (time.perf_counter() - start_time < self.game_timeout * 60):
                self.finish('game timed out')
                break
            self.update()
            elapsed_time = time.perf_counter() - last_frame_time
            time_to_wait = (1 / 60) - elapsed_time
            if time_to_wait > 0:
                time.sleep(time_to_wait)
            last_frame_time = time.perf_counter()

    def launch(self):
        from game_server.server import Server
        timeout = os.environ.get('GAME_PLAYER_CONNECT_TIMEOUT', 5)
        try:
            timeout = float(timeout)
        except ValueError:
            timeout = 5
        try:
            self.wait_for_players(timeout)
            print(time.time(), "all players are connected", flush=True)
        except self.PlayerTimeout as e:
            print(e, flush=True)
            self.finish(FinishReason.PLAYER_NOT_CONNECTED)
            print('game canceled', flush=True)
            return
        if (self.match.game_mode == 'clash'): #watchout for 'clash'
            self.canvas = Position(1800, 750)
            self.send_rackets()
        self.send_canvas()
        self.send_game_state()
        print('game launched', flush=True)
        self.play()
        print('game finished', flush=True)

    def disconnect_players(self, disconnected_user_id: int | None = None):
        from game_server.server import Server
        players = []
        disc_sid = None
        for team in self.match.teams:
            for player in team.players:
                if player.user_id == disconnected_user_id:
                    disc_sid = player.socket_id
                players.append(player)
        Server.disconnect(players, disc_sid)

    def finish(self, finish_reason: str, winner: str | None = None, disconnected_user_id: int | None = None):
        from game_server.server import Server
        print('finishing game', flush=True)
        self.send_finish(finish_reason, winner)
        if (finish_reason == FinishReason.PLAYER_ABANDON):
            self.disconnect_players()
        else:
            self.disconnect_players(disconnected_user_id)
        self.finished = True
        Server.delete_game(self.match.id)
        if (disconnected_user_id is not None):
            finish_match(self.match.id, finish_reason, disconnected_user_id)

    def reset_game_state(self):
        # print('reset_game_state', flush=True)
        self.ball = self.create_ball(self.canvas)
        self.ball.last_touch_team_a = self.match.teams[0].players[0].user_id
        self.ball.last_touch_team_b = self.match.teams[1].players[0].user_id
        for racket in self.rackets:
            racket.position.y = int(self.canvas.y - racket.height) // 2
            racket.velocity = 0
            racket.block_glide = False

    def score(self, team):
        from game_server.server import Server
        last_touch = self.ball.last_racket_touched
        if last_touch is not None:
            last_touch = self.get_player(last_touch)
            if last_touch.team == team:
                # last player to touch the ball was from the scoring team
                last_touch.score_goal()
            else:
                # last player to touch the ball self scored
                last_touch.score_goal(csc=True)
                team.score += 1
        else:
            # handle case where no one touched the ball
            try:
                if (team.name == 'a'):
                    self.get_player(self.ball.last_touch_team_a).score_goal()
                else:
                    self.get_player(self.ball.last_touch_team_b).score_goal()
            except self.NoSuchPlayer as e:
                print(e, flush=True)
                self.finish(FinishReason.PLAYER_DISCONNECT, team.name)
                return
        self.send_score(team)
        for team in self.match.teams:
            if (team.score == 3):
                self.finish(FinishReason.NORMAL_END, team.name)
                return
        self.reset_game_state()
        self.send_game_state()
        start_time = time.perf_counter()
        self.send_start_countdown()
        effective_start_time = start_time + 2
        self.last_update = 0
        while time.perf_counter() < effective_start_time:
            time.sleep(1 / 120)
        self.send_start_game()

################--------senders--------################

    def send_score(self, scorer_team):
        from game_server.server import Server
        Server.emit('score', data={
            'team_a': self.match.teams[0].score,
            'team_b': self.match.teams[1].score,
        }, room=str(self.match.id))

    def send_finish(self, finish_reason: str | None = None, winner: str | None = None):
        from game_server.server import Server
        async_to_sync(Server._sio.emit)('game_over', data={"reason":finish_reason, "winner":winner}, room=str(self.match.id))

    def send_start_game(self):
        from game_server.server import Server
        Server.emit('start_game', room=str(self.match.id))

    def send_start_countdown(self):
        from game_server.server import Server
        Server.emit('start_countdown', room=str(self.match.id))

    def send_canvas(self):
        from game_server.server import Server
        Server.emit(
            'canvas',
            data={
                'canvas_width': self.canvas.x,
                'canvas_height': self.canvas.y
            },
            room=str(self.match.id)
        )

    def get_game_state(self, side: int):
        if side == 1:
            return {
                'position_x': self.ball.position.x,
                'position_y': self.ball.position.y,
                'direction_x': self.ball.speed_x,
                'direction_y': self.ball.speed_y,
                'speed': self.ball.speed,
            }
        else:
            return {
                'position_x': self.canvas.x - self.ball.position.x - self.ball.size,
                'position_y': self.ball.position.y,
                'direction_x': -self.ball.speed_x,
                'direction_y': self.ball.speed_y,
                'speed': self.ball.speed,
            }

    def send_team(self):
        from game_server.server import Server
        team_str = 'team_a'
        for team in self.match.teams:
            for player in team.players:
                Server.emit('team_id', data={'team': team_str}, to=player.socket_id)
            team_str = 'team_b'

    def send_game_state(self):
        from game_server.server import Server
        side = 1
        for team in self.match.teams:
            for player in team.players:
                Server.emit(
                    'game_state',
                    data=self.get_game_state(side),
                    to=player.socket_id
                )
            side = -1

    def get_rackets(self, side: int):
        rackets = {}
        for racket in self.rackets:
            if side == 1:
                rackets[racket.player_id] = racket.position
            else:
                rackets[racket.player_id] = racket.position.invert(self.canvas.x)

    def send_rackets(self):
        from game_server.server import Server
        side = 1
        for team in self.match.teams:
            for player in team.players:
                Server.emit(
                    'rackets',
                    data=self.get_rackets(side),
                    to=player.socket_id
                )
            side = -1
