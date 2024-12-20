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

    def update(self):
        self.position.y += self.velocity
