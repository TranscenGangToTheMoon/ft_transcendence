from game_server.pong_position import Position


class Ball:
    def __init__(self, position: Position, direction_x, direction_y, speed, size, ledge_offset, racket_width, canvas):
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
        self.canvas = canvas
        self.safe_zone_width = (self.canvas.x / 2) - (ledge_offset + (3 * racket_width))
        self.safe_zone_height = (self.canvas.y / 2) - (3 * self.size)

    def increment_speed(self, max_speed, speed_increment):
        self.speed += speed_increment
        if (self.speed > max_speed):
            self.speed = max_speed

    def is_in_safe_zone(self):
        return abs(self.position.x - self.canvas.x / 2) < self.safe_zone_width and abs(self.position.y - self.canvas.y / 2) < self.safe_zone_height
