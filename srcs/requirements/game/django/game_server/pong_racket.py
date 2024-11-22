from pong_position import Position


class Racket:
    def __init__(self,
        player_id: int,
        socket_id: int,
        position: Position,
        width: int,
        height: int) -> None:
        self.player = player_id
        self.socket_id = socket_id
        self.height = height
        self.width = width
        self.position = position
        self.velocity = 0

    def move_up(self):
        self.velocity = 1

    def move_down(self):
        self.velocity = -1
