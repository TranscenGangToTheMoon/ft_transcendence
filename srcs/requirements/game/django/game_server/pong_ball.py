from game_server.pong_position import Position

class Ball:
    def __init__(self, position: Position, direction: Position) -> None:
        self.position = position
