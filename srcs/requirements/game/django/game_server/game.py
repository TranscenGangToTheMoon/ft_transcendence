from asgiref.sync import async_to_sync
from datetime import datetime, timezone
from game_server.match import Match, Player, finish_match
from game_server.pong_ball import Ball
from game_server.pong_position import Position
from game_server.pong_racket import Racket
from lib_transcendence.exceptions import GameMode
from lib_transcendence.game import FinishReason
from typing import List
import asyncio
import json
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
    default_ball_speed: int
    ball_size: int

    @staticmethod
    def create_ball(canvas: Position):
        direction_x, direction_y = get_random_direction()
        return Ball(Position(int(canvas.x / 2 - (Game.ball_size / 2)), int(canvas.y / 2 - (Game.ball_size / 2))), direction_x, direction_y, Game.default_ball_speed, Game.ball_size)

    @staticmethod
    def create_rackets(match,
                       canvas,
                       racket_height,
                       racket_width,
                       ledge_offset,
                       racket_to_racket_offset) -> List[Racket]:
        rackets: List[Racket] = []
        racket_offset = ledge_offset
        with open('game_server/gameConfig.json', 'r') as config_file:
            config = json.load(config_file)
            racket_max_speed = config['paddle'][match.game_type]['speed']
        # create rackets for right players
        for player in match.teams[0].players:
            racket = Racket(player.user_id, Position(canvas.x - racket_width - racket_offset, int(canvas.y / 2 - racket_height / 2)), racket_height, racket_width, racket_max_speed)
            player.racket = racket
            rackets.append(racket)
            racket_offset += racket_to_racket_offset
        # create rackets for left players
        racket_offset = ledge_offset
        for player in match.teams[1].players:
            racket = Racket(player.user_id, Position(racket_offset, int(canvas.y / 2 - racket_height / 2)), racket_height, racket_width, racket_max_speed)
            player.racket = racket
            rackets.append(racket)
            racket_offset += racket_to_racket_offset
        return rackets

    def __init__(self,
                sio,
                match) -> None:
        self.match: Match = match
        with open('game_server/gameConfig.json', 'r') as config_file:
            config = json.load(config_file)
            self.canvas = Position(config['canvas'][self.match.game_type]['width'],
                                    config['canvas'][self.match.game_type]['height'])
            self.racket_height = config['paddle'][self.match.game_type]['height']
            self.racket_width = config['paddle'][self.match.game_type]['width']
            self.max_score = config['score']['max']
            self.max_bounce_angle = config['ball']['maxBounceAngle']
            self.max_ball_speed = config['ball']['maxSpeed']
            self.speed_increment = config['ball']['speedIncrement']
            self.ledge_offset = config['paddle'][self.match.game_type]['ledgeOffset']
            self.racket_to_racket_offset = config['paddle'][self.match.game_type]['paddleOffset']
        self.finished = False
        self.ball = self.create_ball(self.canvas)
        self.rackets = self.create_rackets(self.match, self.canvas, self.racket_height, self.racket_width, self.ledge_offset, self.racket_to_racket_offset)
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
        elif ball_pos_y + self.ball.size >= self.canvas.y:
            self.ball.position.y -= (ball_pos_y + self.ball.size) - self.canvas.y
            self.ball.speed_y = - self.ball.speed_y

    def handle_goal(self):
        if self.ball.position.x + self.ball.size < 0:
            self.score(self.match.teams[0])
        elif self.ball.position.x > self.canvas.x:
            self.score(self.match.teams[1])

    def calculateImpactPosition(self, ballY, paddleY, paddleHeight):
        relativeY = (paddleY + paddleHeight / 2) - ballY
        return relativeY / (paddleHeight / 2)

    def calculateNewBallDirection(self, paddleY, height):
        impactPosition = self.calculateImpactPosition(self.ball.position.y + self.ball.size / 2, paddleY, height)
        bounceAngle = impactPosition * self.max_bounce_angle

        speed = self.ball.speed
        xNewSpeed = speed * math.cos(bounceAngle)
        yNewSpeed = speed * -math.sin(bounceAngle)
        self.ball.speed_x = -xNewSpeed if self.ball.speed_x < 0 else xNewSpeed
        self.ball.speed_y = yNewSpeed

    def handle_racket_bounce(self, racket):
        if (racket.block_glide):
            self.ball.speed_y = -self.ball.speed_y
            if (abs(self.ball.position.y - racket.position.y + racket.height) <
                abs(self.ball.position.y - racket.position.y)):
                self.ball.position.y = racket.position.y + racket.height
            else:
                self.ball.position.y = racket.position.y - self.ball.size
        else:
            self.ball.speed_x = -self.ball.speed_x
            self.ball.increment_speed(self.max_ball_speed, self.speed_increment)
            self.calculateNewBallDirection(racket.position.y, racket.height)

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
            if (not racket.block_glide):
                if (self.ball.position.x + self.ball.size > racket.position.x and
                    self.ball.position.x + self.ball.size < racket.position.x + racket.width
                ):
                    self.ball.position.x = racket.position.x - self.ball.size;
                else:
                    self.ball.position.x = racket.position.x + racket.width;
        else:
            is_ball_x_in_racket_range = self.ball.position.x < racket.position.x + racket.width and self.ball.position.x + self.ball.size > racket.position.x
            if (is_ball_x_in_racket_range):
                racket.block_glide = True
            else:
                racket.block_glide = False

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
        if self.sending == 0:
            self.send_game_state()
            self.sending = 1
        else:
            self.sending = 0
        self.handle_goal()

################--------game events handling--------################

    def wait_for_players(self, timeout: float):
        start_waiting = time.time()
        for team in self.match.teams:
            for player in team.players:
                while player.socket_id == '':
                    if time.time() - start_waiting > timeout:
                        exception = self.PlayerTimeout('player socketio connection timed out')
                        exception.args = (player.user_id,)
                        raise exception
                    time.sleep(0.1)

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
            self.finish(FinishReason.PLAYER_NOT_CONNECTED, disconnected_user_id=e.args[0])
            return
        if (self.match.game_type == '3v3'):
            self.send_rackets()
        self.send_canvas()
        self.send_game_state()
        self.play()

    def disconnect_players(self, disconnected_user_id: int | None = None):
        from game_server.server import Server
        players = []
        disc_sid = None
        for team in self.match.teams:
            for player in team.players:
                if player.user_id == disconnected_user_id:
                    disc_sid = player.socket_id
                players.append(player)
        Server.disconnect(players=players, disconnected_sid=disc_sid)

    def finish(self,
            finish_reason: str,
            winner: str | None = None,
            disconnected_user_id: int | None = None,
            error=False):
        from game_server.server import Server
        self.send_finish(finish_reason, winner)
        if (finish_reason == FinishReason.PLAYER_DISCONNECT and disconnected_user_id is not None):
            self.disconnect_players(disconnected_user_id)
        else:
            self.disconnect_players()
        self.finished = True
        Server.delete_game(self.match.id)
        if (disconnected_user_id is not None and error == False):
            finish_match(self.match.id, finish_reason, disconnected_user_id)

    def reset_game_state(self):
        self.ball = self.create_ball(self.canvas)
        self.ball.last_touch_team_a = self.match.teams[0].players[0].user_id
        self.ball.last_touch_team_b = self.match.teams[1].players[0].user_id
        for racket in self.rackets:
            racket.position.y = int(self.canvas.y - racket.height) // 2
            racket.velocity = 0
            racket.block_glide = False

    def get_scorer(self, team):
        last_touch = self.ball.last_racket_touched
        if last_touch is not None:
            last_touch = self.get_player(last_touch)
            if last_touch.team == team:
                # last player to touch the ball was from the scoring team
                return last_touch, False
            else:
                # last player to touch the ball self scored
                return last_touch, True
        else:
            # handle case where no one touched the ball
            try:
                if (team.name == 'a'):
                    return self.get_player(self.ball.last_touch_team_a), False
                else:
                    return self.get_player(self.ball.last_touch_team_b), False
            except self.NoSuchPlayer as e:
                print(e, flush=True)
                self.finish(FinishReason.PLAYER_DISCONNECT, team.name)
                return

    def get_other_team(self, team):
        return self.match.teams[0] if team == self.match.teams[1] else self.match.teams[1]

    def score(self, team):
        scorer = self.get_scorer(team)
        if scorer is None:
            return # game finished
        scorer, csc = scorer
        updated_game_instance = scorer.score_goal(csc)
        if updated_game_instance is None:
            self.finish('Server Error', team.name, error=True)
            return
        self.match.teams[0].score = updated_game_instance['teams']['a']['score']
        self.match.teams[1].score = updated_game_instance['teams']['b']['score']
        self.send_score(updated_game_instance)
        if updated_game_instance['finished'] == True:
            self.finish(FinishReason.NORMAL_END, updated_game_instance['winner'])
        else:
            # launch a new point
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

    def send_score(self, game_instance):
        from game_server.server import Server
        Server.emit('score', data={
            'team_a': game_instance['teams']['a']['score'],
            'team_b': game_instance['teams']['b']['score'],
        }, room=str(self.match.id))

    def send_finish(self, finish_reason: str | None = None, winner: str | None = None):
        from game_server.server import Server
        async_to_sync(Server._sio.emit)('game_over', data={"reason":finish_reason, "winner":winner}, room=str(self.match.id))

    def send_start_game(self):
        from game_server.server import Server
        self.sending = 0
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
                'speed_x': self.ball.speed_x,
                'speed_y': self.ball.speed_y,
                'speed': self.ball.speed,
            }
        else:
            return {
                'position_x': self.canvas.x - self.ball.position.x - self.ball.size,
                'position_y': self.ball.position.y,
                'speed_x': -self.ball.speed_x,
                'speed_y': self.ball.speed_y,
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
            print(f"racket = {racket.position.x}", flush=True)
            if side == 1:
                rackets[racket.player_id] = racket.position.x
            else:
                rackets[racket.player_id] = racket.position.invert(self.canvas.x).x - racket.width
        return rackets

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
