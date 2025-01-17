from game_server.pong_position import Position
import os


class Racket:
    # TODO -> add height and width to racket from env
    height: int
    width: int
    height_3v3: int
    width_3v3: int
    max_speed: int
    def __init__(self,
                 player: int,
                 position: Position) -> None:
        self.player_id = player
        self.position = position
        self.velocity = 0
        self.height = Racket.height
        self.width = Racket.width
        self.block_glide = False

    def move_up(self):
        self.velocity = -1

    def move_down(self):
        self.velocity = 1

    def stop_moving(self, y):
        self.velocity = 0
        if (abs(y - self.position.y) < 10):
            self.position.y = y
        return self.position.y

    def update(self, ball_size, canvas_height, time_delta):
        self.position.y += self.velocity * Racket.max_speed * time_delta
        if self.block_glide:
            if self.position.y + self.height + ball_size < canvas_height:
                self.position.y = canvas_height - self.height - ball_size
            elif self.position.y - ball_size > 0:
                self.position.y = ball_size
        if self.position.y < 0:
            self.position.y = 0
        elif self.position.y + self.height > canvas_height:
            self.position.y = canvas_height - self.height
