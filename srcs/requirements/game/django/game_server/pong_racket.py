from pong_position import Position
from pong_player import Player


class Racket:
    def __init__(self,
                 player: Player,
                 position: Position,
                 width: int = 800,
                 height: int = 600) -> None:
        self.player = player
        self.height = height
        self.width = width
        self.position = position
        self.velocity = 0

    def move_up(self):
        self.velocity = 1

    def move_down(self):
        self.velocity = -1

    def update(self):
        self.position.y += self.velocity
