from typing import List
from pong_ball import Ball
from pong_racket import Racket
from pong_position import Position
from pong_player import Team


def get_random_direction() -> Position:
    return Position(0, 0)

class Game:
    def __init__(self,
                 team_a: Team,
                 team_b: Team,
                 canvas_size: Position) -> None:
        direction = get_random_direction()
        self.ball = Ball(Position(int(canvas_size.x / 2), int(canvas_size.y / 2)), direction)
        racket_size: Position = Position(10, 100)
        self.rackets: List[Racket] = []
        for player in team_a.players:
            self.rackets.append(Racket(player, Position(0, int(canvas_size.y / 2 - racket_size.y / 2)), racket_size.x, racket_size.y))
        for player in team_b.players:
            self.rackets.append(Racket(player, Position(canvas_size.x - racket_size.x, int(canvas_size.y / 2 - racket_size.y / 2)), racket_size.x, racket_size.y))

    def move_racket(self, socket_id):
        pass

    def update(self):
        pass
