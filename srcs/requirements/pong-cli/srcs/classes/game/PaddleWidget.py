# Textual imports
from textual.geometry   import Offset
from textual.widget     import Widget

# Local imports
from classes.utils.config   import Config

class Paddle(Widget):
    def __init__(self, side = "right"):
        super().__init__()
        self.styles.width = Config.Paddle.width
        self.styles.height = Config.Paddle.height
        if side == "left":
            self.styles.layer = "1"
            self.styles.background = "white"
            self.offset = Offset(Config.Paddle.gap, (Config.Playground.height - Config.Paddle.height) // 2)
        elif side == "right":
            self.styles.layer = "2"
            self.styles.background = "white"
            self.offset = Offset(Config.Playground.width - Config.Paddle.gap - Config.Paddle.width, (Config.Playground.height - Config.Paddle.height) // 2)

    def render(self):
        return " " * Config.Paddle.height * Config.Paddle.width
        # return "█" * Config.Paddle.height * Config.Paddle.width

    def moveUp(self):
        if self.offset.y > 0:
            self.offset -= Offset(0, Config.Paddle.speed)

    def moveDown(self):
        if self.offset.y < 40 - Config.Paddle.height:
            self.offset += Offset(0, Config.Paddle.speed)
