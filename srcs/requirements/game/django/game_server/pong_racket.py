from game_server.pong_position import Position


class Racket:
    def __init__(self,
                 player: int,
                 position: Position,
                 width: int = 10,
                 height: int = 100) -> None:
        self.player_id = player
        self.height = height
        self.width = width
        self.position = position
        self.velocity = 0

    def move_up(self):
        self.velocity = -1

    def move_down(self):
        self.velocity = 1

    def stop_moving(self):
        self.velocity = 0

    def update(self):
        self.position.y += self.velocity
