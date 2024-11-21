from typing import Dict, List
from pong_ball import Ball
from pong_racket import Racket
from pong_position import Position
from pong_player import Player, Team


def get_random_direction() -> Position:
    return Position(0, 0)

class Game:
    def __init__(self,
            team_a: Team,
            team_b: Team,
            canvas_size: Position) -> None:
        direction = get_random_direction()
        self.ball = Ball(Position(int(canvas_size.x / 2), int(canvas_size.y / 2)), direction)
        self.rackets: List[Racket] = []
        for player in players:
            self.rackets.append(Racket(player.id, player.sid, Position))

    def move_racket(self, socket_id):
        pass

    def update(self):
        pass
