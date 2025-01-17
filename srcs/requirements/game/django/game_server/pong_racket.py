from game_server.pong_position import Position
import os


class Racket:
    width: int
    def __init__(self,
                 player: int,
                 position: Position,
                 racket_height,
                 racket_width,
                 max_speed) -> None:
        self.player_id = player
        self.position = position
        self.velocity = 0
        self.height = racket_height
        self.width = racket_width
        self.block_glide = False
        self.max_speed = max_speed

    def move_up(self):
        self.velocity = -1

    def move_down(self):
        self.velocity = 1

    def stop_moving(self, y):
        self.velocity = 0
        if (abs(y - self.position.y) < 15):
            self.position.y = y
        return self.position.y

    def update(self, ball_size, canvas_height, time_delta):
        self.position.y += self.velocity * self.max_speed * time_delta
        if self.block_glide:
            if self.position.y + self.height + ball_size < canvas_height:
                self.position.y = canvas_height - self.height - ball_size
            elif self.position.y - ball_size > 0:
                self.position.y = ball_size
        if self.position.y < 0:
            self.position.y = 0
        elif self.position.y + self.height > canvas_height:
            self.position.y = canvas_height - self.height
