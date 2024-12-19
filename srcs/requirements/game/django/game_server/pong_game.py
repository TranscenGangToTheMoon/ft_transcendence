from datetime import datetime, timezone
import math
from game_server.match import Match, Player, finish_match
from game_server.pong_ball import Ball
from game_server.pong_position import Position
from game_server.pong_racket import Racket
from typing import List
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
        # create rackets for right players
        for player in match.teams[0].players:
            racket = Racket(player.user_id, Position(0, int(canvas.y / 2 - racket_size.y / 2)), racket_size.x, racket_size.y)
            player.racket = racket
            rackets.append(racket)
        # create rackets for left players
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

    def calculateImpactPosition(self, ballY, paddleY, paddleHeight):
        const relativeY = (paddleY + paddleHeight / 2) - ballY
        return relativeY / (paddleHeight / 2)

    def calculateNewBallDirection(self, paddleY):
        impactPosition = self.calculateImpactPosition(self.ball.position.y + self.ball.size / 2, paddleY, Racket.height)
        bounceAngle = impactPosition * self.max_bounce_angle

        speed = self.ball.speed
        xNewSpeed = speed * math.cos(bounceAngle)
        yNewSpeed = speed * -math.sin(bounceAngle)
        self.ball.speed_x = self.ball.speed_x < 0 ? xNewSpeed * -1 : xNewSpeed
        self.ball.speed_y = yNewSpeed

    def handle_racket_bounce(self, racket):
        if (racket.blockGlide){
            self.ball.speed_y = -self.ball.speed_y;
            if (abs(self.ball.y - (racket.y + racket.height)) <
                abs(self.ball.y - (racket.y)))
                self.ball.y = racket.y + racket.height;
            else
                self.ball.y = racket.y - self.ball.size;
        }
        else{
            self.ball.speedX = -self.ball.speedX;
            self.ball.increment_speed(self.max_ball_speed, self.speed_increment);
            self.calculateNewBallDirection(racket.y);
        }
        # if (paddle == state.paddles.right) {
        #     if (typeof socket !== 'undefined')
        #         window.socket.emit('bounce', {'dir_x': state.ball.speedX, 'dir_y': state.ball.speedY})
        # }

    def handle_racket_collision(self, racket):
        ball_is_right_from_racket = self.ball.position.x < racket.position.x + racket.width && self.ball.position.x > racket.position.x;
        ball_is_left_from_racket = self.ball.position.x + self.ball.size > racket.position.x && self.ball.position.x + self.ball.size < racket.position.x + racket.width;
        is_ball_y_in_paddle_range = self.ball.position.y + self.ball.size > racket.position.y && self.ball.position.y < racket.position.y + racket.height;

        if ((ball_is_left_from_racket || ball_is_right_from_racket) && is_ball_y_in_paddle_range){
            self.handle_racket_bounce(racket);
            if (!racket.blockGlide){
                if (self.ball.position.x + self.ball.size > racket.position.x &&
                    self.ball.position.x + self.ball.size < racket.position.x + racket.width
                ){
                    self.ball.position.x = racket.position.x - self.ball.size;
                }
                else{
                    self.ball.position.x = racket.position.x + racket.width;
                }
            }
        }
        else {
            is_ball_x_in_paddle_range = self.ball.position.x < paddle.x + racket.width && self.ball.position.x + self.ball.size > paddle.x
            if (is_ball_x_in_paddle_range)
                paddle.blockGlide = true;
            else
                paddle.blockGlide = false;
        }
        # for paddle in self.rackets:
        #     if paddle.block_glide:
        #         self.ball.direction_y = -self.ball.direction_y
        #         if abs(self.ball.position.y - (paddle.position.y + paddle.height)) < abs(self.ball.position.y - paddle.position.y):
        #             self.ball.position.y = paddle.position.y + paddle.height
        #         else:
        #             self.ball.position.y = paddle.position.y - self.ball.size
        #     else:
        #         self.ball.direction_x = -self.ball.direction_x
        #         # if self.ball.speed < self.max_ball_speed:
        #         #     self.increment_ball_speed()
        #         self.calculate_new_ball_direction(paddle.position.y)
        #         self.sio.emit('bounce', {'dir_x': self.ball.direction_x, 'dir_y': self.ball.direction_y})

    def update(self):
        for racket in self.rackets:
            racket.update()
            self.handle_racket_collision(racket);
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

    def send_canvas(self):
        from game_server.server import Server
        Server.emit(
            'game_state',
            data={
                'canvas_width': self.canvas.x,
                'canvas_height': self.canvas.y
            },
            room=str(self.match.id)
        )

    def send_game_state(self):
        from game_server.server import Server
        side = 1
        for team in self.match.teams:
            for player in team.players:
                Server.emit(
                    'game_state',
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

    def send_start_game(self):
        from game_server.server import Server
        Server.emit('start_game', room=str(self.match.id))
        print('emitted start_game', flush=True)

    def play(self):
        from game_server.server import Server
        start_time = time.time()
        last_frame_time = start_time
        self.send_start_game()
        while True:
            if self.game_timeout is not None and (time.time() - start_time < self.game_timeout * 60):
                break
            while time.time() - last_frame_time < (1 / 60):
                time.sleep(0.005)
            self.update()
            last_frame_time = time.time()
        self.finish()
        Server.delete_game(self.match.id)

    def launch(self):
        from game_server.server import Server
        try:
            timeout = int(os.environ['GAME_PLAYER_CONNECT_TIMEOUT'])
        except KeyError:
            timeout = 5
        print(time.time(), "launch()", flush=True)
        timeout = 60.
        try:
            self.wait_for_players(timeout)
            print(time.time(), "all players are connected", flush=True)
        except Exception as e:
            print(e, flush=True)
            self.finish('game timed out, not all players connected to server')
            print('game canceled', flush=True)
            return
        self.send_canvas()
        self.send_game_state()
        print('game launched', flush=True)
        self.play()

    def check_zombie(self) -> bool:
        if self.match.model.finished:
            return True
        game_start_time: datetime = self.match.model.created_at
        game_timeout = self.match.model.game_duration
        now = datetime.now(timezone.utc)
        if game_start_time <= now - game_timeout:
            self.match.model.finish_match('game cancelled') # TODO -> ask flo for more details on what to set as reason
            print('finished match', self.match.id)
            return True
        return False

    def finish(self, reason: str | None = None):
            self.match.model.finish_match(reason)

    def score(self, player):
        from game_server.server import Server
        last_touch: Player | None = self.ball.last_racket_touched
        if last_touch is not None:
            last_touch.csc += 1
        self.ball.position = Position(int(self.canvas.x / 2), int(self.canvas.y / 2))
        self.ball.direction_x, self.ball.direction_y = get_random_direction()
        for team in self.match.teams:
            if (player.team == team):
                if (team.score == 4):
                    self.finish()
        self.send_game_state()
