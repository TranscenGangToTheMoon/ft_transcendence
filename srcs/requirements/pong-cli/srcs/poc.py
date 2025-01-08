from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static
import asyncio
import random
import math

CONFIG = {
    "width": 80,
    "height": 20,
    "paddle_width": 1,
    "paddle_height": 5,
    "ball_size": 1,
    "max_ball_speed": 1.5,
    "default_ball_speed": 0.4,
    "ball_speed_increment": 0.1,
    "winning_score": 3,
    "max_bounce_angle": 2 * (math.pi / 5)
}

class Position:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class Paddle(Static):
    DEFAULT_CSS = f"""
    Paddle {{
        width: {CONFIG['paddle_width']};
        height: {CONFIG['paddle_height']};
        background: white;
        dock: left;
    }}
    """

    def __init__(self, side="left"):
        super().__init__("")
        self.side = side
        if side == "right":
            self.styles.dock = "right"
        self.position = (CONFIG['height'] - CONFIG['paddle_height']) // 2
        self.speed = 2

    def move_up(self):
        if self.position > 0:
            self.position -= self.speed
            self.styles.margin = (self.position, 0)

    def move_down(self, max_height):
        if self.position < max_height - CONFIG['paddle_height']:
            self.position += self.speed
            self.styles.margin = (self.position, 0)

class Ball(Static):
    DEFAULT_CSS = f"""
    Ball {{
        width: {CONFIG['ball_size']};
        height: {CONFIG['ball_size']};
        background: black;
    }}
    """

    def __init__(self):
        super().__init__("●")
        self.position = Position(CONFIG['width'] // 2, CONFIG['height'] // 2)
        self.speed = CONFIG['default_ball_speed']
        self.dx = self.speed
        self.dy = self.speed

    def move(self):
        self.position.x += self.dx
        self.position.y += self.dy
        self.styles.margin = (int(self.position.y), 0, 0, int(self.position.x))

class Score(Static):
    CSS = """
    Score {
        dock: top;
        width: 100%;
        height: 1;
        content-align: center middle;
    }
    """

    def __init__(self):
        super().__init__("0 - 0")
        self.left_score = 0
        self.right_score = 0

    def update_score(self, player: str):
        if player == "left":
            self.left_score += 1
        else:
            self.right_score += 1
        self.update(f"{self.left_score} - {self.right_score}")

class PongGame(App):
    CSS = """
    Screen {
        background: #000000;
    }
    Container {
        outline: inner red;
        margin: 0;
        padding: 0;
        border: green;
        border: panel;
        layers: base;
        width: 82;
        height: 22;
    }
    """

    def __init__(self):
        super().__init__()
        self.paddle_left = Paddle("left")
        self.paddle_right = Paddle("right")
        self.ball = Ball()
        self.score = Score()
        self.run_game = True

    def compose(self) -> ComposeResult:
        yield self.score
        yield Container(
            self.paddle_left,
            self.paddle_right,
            self.ball,
        )

    async def on_mount(self) -> None:
        asyncio.create_task(self.game_loop())

    def on_key(self, event) -> None:
        if event.key == "w":
            self.paddle_left.move_up()
        elif event.key == "s":
            self.paddle_left.move_down(CONFIG['height'])
        elif event.key == "up":
            self.paddle_right.move_up()
        elif event.key == "down":
            self.paddle_right.move_down(CONFIG['height'])
        elif event.key == "q":
            self.run_game = False
            self.exit()

    def check_collision(self) -> bool:
        if self.ball.position.y <= 0 or self.ball.position.y >= CONFIG['height'] - 1:
            self.ball.dy *= -1

        paddle_left_x = 1
        paddle_right_x = CONFIG['width'] - 2

        if (self.ball.position.x <= paddle_left_x + 1 and
                self.paddle_left.position <= self.ball.position.y <= self.paddle_left.position + CONFIG['paddle_height']):
            relative_intersect_y = (self.paddle_left.position + CONFIG['paddle_height']/2) - self.ball.position.y
            normalized_intersect = relative_intersect_y / (CONFIG['paddle_height']/2)
            bounce_angle = normalized_intersect * CONFIG['max_bounce_angle']
            self.ball.dx = abs(self.ball.speed * math.cos(bounce_angle))
            self.ball.dy = -self.ball.speed * math.sin(bounce_angle)
            self.ball.speed = min(self.ball.speed + CONFIG['ball_speed_increment'], CONFIG['max_ball_speed'])
            return True

        if (self.ball.position.x >= paddle_right_x - 1 and
                self.paddle_right.position <= self.ball.position.y <= self.paddle_right.position + CONFIG['paddle_height']):
            relative_intersect_y = (self.paddle_right.position + CONFIG['paddle_height']/2) - self.ball.position.y
            normalized_intersect = relative_intersect_y / (CONFIG['paddle_height']/2)
            bounce_angle = normalized_intersect * CONFIG['max_bounce_angle']
            self.ball.dx = -abs(self.ball.speed * math.cos(bounce_angle))
            self.ball.dy = -self.ball.speed * math.sin(bounce_angle)
            self.ball.speed = min(self.ball.speed + CONFIG['ball_speed_increment'], CONFIG['max_ball_speed'])
            return True

        if self.ball.position.x < 0:
            self.score.update_score("right")
            self.reset_ball()
        elif self.ball.position.x > CONFIG['width']:
            self.score.update_score("left")
            self.reset_ball()

        return False

    def reset_ball(self):
        self.ball.position = Position(CONFIG['width'] // 2, CONFIG['height'] // 2)
        self.ball.speed = CONFIG['default_ball_speed']
        self.ball.dx = self.ball.speed * random.choice([-1, 1])
        self.ball.dy = self.ball.speed * random.choice([-1, 1])

    async def game_loop(self):
        while self.run_game:
            self.ball.move()
            self.check_collision()
            await asyncio.sleep(0.040)

if __name__ == "__main__":
    app = PongGame()
    app.run()

####
def handle_wall_bounce(self):
    ball_pos_y = self.ball.position.y
    if ball_pos_y <= 0:
        self.ball.position.y = - ball_pos_y
        self.ball.speed_y = - self.ball.speed_y
        print('bouncing up', flush=True)
    elif ball_pos_y + self.ball.size >= self.canvas.y:
        self.ball.position.y -= (ball_pos_y + self.ball.size) - self.canvas.y
        self.ball.speed_y = - self.ball.speed_y
        print('bouncing down', flush=True)

def handle_goal(self):
    if self.ball.position.x + self.ball.size < 0:
        self.score(self.match.teams[1])
    elif self.ball.position.x > self.canvas.x:
        self.score(self.match.teams[0])

def calculateImpactPosition(self, ballY, paddleY, paddleHeight):
    relativeY = (paddleY + paddleHeight / 2) - ballY
    return relativeY / (paddleHeight / 2)

def calculateNewBallDirection(self, paddleY):
    impactPosition = self.calculateImpactPosition(self.ball.position.y + self.ball.size / 2, paddleY, Racket.height)
    bounceAngle = impactPosition * self.max_bounce_angle

    speed = self.ball.speed
    xNewSpeed = speed * math.cos(bounceAngle)
    yNewSpeed = speed * -math.sin(bounceAngle)
    self.ball.speed_x = -xNewSpeed if self.ball.speed_x < 0 else xNewSpeed
    self.ball.speed_y = yNewSpeed

def handle_racket_bounce(self, racket):
    if (racket.blockGlide):
        self.ball.speed_y = -self.ball.speed_y
        self.ball.direction_y = -self.ball.direction_y
        if (abs(self.ball.position.y - (racket.position.y + racket.height)) <
                abs(self.ball.position.y - (racket.position.y))):
            self.ball.position.y = racket.position.y + racket.height
        else:
            self.ball.position.y = racket.position.y - self.ball.size
    else:
        self.ball.speed_x = -self.ball.speed_x
        self.ball.direction_x = -self.ball.direction_x
        self.ball.increment_speed(self.max_ball_speed, self.speed_increment)
        self.calculateNewBallDirection(racket.position.y)

def handle_racket_collision(self, racket):
    ball_is_right_from_racket = self.ball.position.x < racket.position.x + racket.width and self.ball.position.x > racket.position.x
    ball_is_left_from_racket = self.ball.position.x + self.ball.size > racket.position.x and self.ball.position.x + self.ball.size < racket.position.x + racket.width
    is_ball_y_in_paddle_range = self.ball.position.y + self.ball.size > racket.position.y and self.ball.position.y < racket.position.y + racket.height

    if (ball_is_left_from_racket == True or ball_is_right_from_racket == True) and is_ball_y_in_paddle_range == True:
        self.handle_racket_bounce(racket)
        self.ball.last_racket_touched = racket.player
        if racket.player.team == self.match.teams[0]:
            self.last_racket_touched_team_a = racket.player
        else:
            self.last_racket_touched_team_b = racket.player
        if (not racket.blockGlide):
            if (self.ball.position.x + self.ball.size > racket.position.x and
                    self.ball.position.x + self.ball.size < racket.position.x + racket.width
            ):
                self.ball.position.x = racket.position.x - self.ball.size;
            else:
                self.ball.position.x = racket.position.x + racket.width;
    else:
        is_ball_x_in_racket_range = self.ball.position.x < racket.position.x + racket.width and self.ball.position.x + self.ball.size > racket.position.x
        if (is_ball_x_in_racket_range):
            racket.blockGlide = True
        else:
            racket.blockGlide = False

def update(self):
    if (self.last_update == 0):
        self.last_update = time.perf_counter()
    time_delta = time.perf_counter() - self.last_update
    self.last_update = time.perf_counter()
    for racket in self.rackets:
        racket.update(self.ball.size, self.canvas.y, time_delta)
    self.ball.position.x += self.ball.speed_x * time_delta
    self.ball.position.y += self.ball.speed_y * time_delta
    self.handle_wall_bounce()
    for racket in self.rackets:
        self.handle_racket_collision(racket)
    self.send_game_state()
    self.handle_goal()