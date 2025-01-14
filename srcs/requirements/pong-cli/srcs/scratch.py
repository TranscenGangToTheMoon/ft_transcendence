from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static
from rich.segment import Segment
import asyncio
import random

class Position:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class Paddle(Static):
    DEFAULT_CSS = """
    Paddle {
        width: 1;
        height: 5;
        background: white;
    }
    """

    def __init__(self):
        super().__init__("")
        self.position = 0
        self.speed = 2

    def move_up(self):
        if self.position > 0:
            self.position -= self.speed
            self.styles.margin = (self.position, 0, 0, 0)

    def move_down(self, max_height):
        if self.position < max_height - 5:  # 5 est la hauteur définie dans le CSS
            self.position += self.speed
            self.styles.margin = (self.position, 0, 0, 0)

class Ball(Static):
    DEFAULT_CSS = """
    Ball {
        width: 1;
        height: 1;
        background: white;
    }
    """

    def __init__(self):
        super().__init__("●")
        self.dx = 1
        self.dy = 1
        self.position = Position(40, 10)
        self.speed = 0.5

    def move(self):
        self.position.x += self.dx * self.speed
        self.position.y += self.dy * self.speed
        self.styles.margin = (int(self.position.y), 0, 0, int(self.position.x))

class Score(Static):
    def __init__(self):
        super().__init__("Score: 0")
        self.value = 0

    def update_score(self, points: int):
        self.value += points
        self.update(f"Score: {self.value}")

class PongGame(App):
    CSS = """
    Screen {
        background: #000000;
    }
    """

    def __init__(self):
        super().__init__()
        self.paddle_left = Paddle()
        self.paddle_right = Paddle()
        self.ball = Ball()
        self.score = Score()
        self.run_game = True

    def compose(self) -> ComposeResult:
        yield Container(
            self.paddle_left,
            self.paddle_right,
            self.ball,
            self.score
        )

    async def on_mount(self) -> None:
        self.paddle_right.styles.margin = (0, 0, 0, self.size.width - 1)
        asyncio.create_task(self.game_loop())

    def on_key(self, event) -> None:
        if event.key == "w":
            self.paddle_left.move_up()
        elif event.key == "s":
            self.paddle_left.move_down(self.size.height)
        elif event.key == "up":
            self.paddle_right.move_up()
        elif event.key == "down":
            self.paddle_right.move_down(self.size.height)
        elif event.key == "q":
            self.run_game = False
            self.exit()

    def check_collision(self) -> bool:
        if self.ball.position.y <= 0 or self.ball.position.y >= self.size.height - 1:
            self.ball.dy *= -1

        if (self.ball.position.x <= 1 and
                self.paddle_left.position <= self.ball.position.y <= self.paddle_left.position + 5):
            self.ball.dx *= -1
            self.score.update_score(1)
            return True

        if (self.ball.position.x >= self.size.width - 2 and
                self.paddle_right.position <= self.ball.position.y <= self.paddle_right.position + 5):
            self.ball.dx *= -1
            self.score.update_score(1)
            return True

        if self.ball.position.x < 0 or self.ball.position.x > self.size.width:
            self.reset_ball()
            return False

        return False

    def reset_ball(self):
        self.ball.position = Position(self.size.width // 2, self.size.height // 2)
        self.ball.dx = random.choice([-1, 1])
        self.ball.dy = random.choice([-1, 1])

    async def game_loop(self):
        while self.run_game:
            self.ball.move()
            self.check_collision()
            await asyncio.sleep(0.05)

if __name__ == "__main__":
    app = PongGame()
    app.run()