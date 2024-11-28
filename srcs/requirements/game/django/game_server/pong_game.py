import socket
from typing import List
from pong_ball import Ball
from pong_racket import Racket
from pong_position import Position

def get_random_direction() -> Position:
    return Position(0, 0)

class Game:
    def __init__(self,
                teams,
                canvas_size: Position) -> None:
        # direction = get_random_direction()
        # self.ball = Ball(Position(int(canvas_size.x / 2), int(canvas_size.y / 2)), direction)

        racket_size: Position = Position(10, 100)
        self.rackets: List[Racket] = []

        # create rackets for left players
        for player in teams[0].players:
            self.rackets.append(Racket(player, Position(0, int(canvas_size.y / 2 - racket_size.y / 2)), racket_size.x, racket_size.y))
        # create rackets for right players
        for player in teams[1].players:
            self.rackets.append(Racket(player, Position(canvas_size.x - racket_size.x, int(canvas_size.y / 2 - racket_size.y / 2)), racket_size.x, racket_size.y))

        # to send : position, direction et vitesse de la balle à 20fps
        # Position des joueurs

        # event -> player_move {player_id: 1231, moving: ['stop', 'up', 'down']}
        # event -> server_update {ball: {x: 3, y: 4, direction: 91823750987}}

    def get_racket(self, socket_id) -> Racket:
        for racket in self.rackets:
            if racket.player.socket_id == socket_id:
                return racket
        raise Exception(f'no racket matching socket id {socket_id}')

    def update(self):
        pass
