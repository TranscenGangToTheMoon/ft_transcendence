from game_server.pong_position import Position

class Ball:
    def __init__(self, position: Position, direction_x, direction_y, speed, size):
        self.speed = speed
        self.position = position
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.size = size
