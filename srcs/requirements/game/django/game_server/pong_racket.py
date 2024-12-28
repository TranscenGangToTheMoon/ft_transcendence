from game_server.pong_position import Position
import os


class Racket:
    # TODO -> add height and width to racket from env
    height: int
    width: int
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
        self.position.y = y

    def update(self, ball_size, canvas_height):
        self.position.y += self.velocity * 5
        if self.block_glide:
            if self.position.y + self.height + ball_size < canvas_height:
                self.position.y = canvas_height - self.height - ball_size
            elif self.position.y - ball_size > 0:
                self.position.y = ball_size
        if self.position.y < 0:
            self.position.y = 0
        elif self.position.y + self.height > canvas_height:
            self.position.y = canvas_height - self.height
