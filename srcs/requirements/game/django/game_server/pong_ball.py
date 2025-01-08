from game_server.pong_position import Position

class Ball:
    def __init__(self, position: Position, direction_x, direction_y, speed, size):
        self.position = position
        self.speed = speed
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.speed_y = speed * direction_y
        self.speed_x = speed * direction_x
        self.size = size
        self.last_racket_touched: int | None = None
        self.last_touch_team_a: int
        self.last_touch_team_b: int
        # TODO -> update and check last_racket_touched to count CSC goals

    def increment_speed(self, max_speed, speed_increment):
        self.speed += speed_increment
        if (self.speed > max_speed):
            self.speed = max_speed
