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
        self.direction = 0
        self.cY = (Config.Playground.cHeight - Config.Paddle.cHeight) // 2
        if side == "left":
            self.styles.layer = "1"
            self.styles.background = "red"

            self.cX = Config.Paddle.cGap
            self.offset = Offset(
                round(self.cX * Config.Playground.width / Config.Playground.cWidth),
                round(self.cY * Config.Playground.height / Config.Playground.cHeight)
            )
        elif side == "right":
            self.styles.layer = "2"
            self.styles.background = "blue"

            self.cX = Config.Playground.cWidth - Config.Paddle.cGap - Config.Paddle.cWidth
            self.offset = Offset(
                round(self.cX * Config.Playground.width / Config.Playground.cWidth),
                round(self.cY * Config.Playground.height / Config.Playground.cHeight)
            )

    def render(self):
        return ""

    def reset(self):
        self.cY = (Config.Playground.cHeight - Config.Paddle.cHeight) // 2
        self.offset = Offset(
            self.offset.x,
            round(self.cY * Config.Playground.height / Config.Playground.cHeight)
        )

    def moveUp(self, dT: float):
        self.direction = -1
        if self.cY - Config.Paddle.cSpeed / dT > 0:
            self.cY -= Config.Paddle.cSpeed / dT
        else:
            self.cY = 0
        self.offset = Offset(
            self.offset.x,
            round(self.cY * Config.Playground.height / Config.Playground.cHeight)
        )

    def moveDown(self, dT: float):
        self.direction = 1
        if self.cY + Config.Paddle.cSpeed / dT < Config.Playground.cHeight - Config.Paddle.cHeight:
            self.cY += Config.Paddle.cSpeed / dT
        else:
            self.cY = Config.Playground.cHeight - Config.Paddle.cHeight
        self.offset = Offset(
            self.offset.x,
            round(self.cY * Config.Playground.height / Config.Playground.cHeight)
        )

    def stopMoving(self, cY: float):
        self.direction = 0
        self.cY = cY
        self.offset = Offset(
            self.offset.x,
            round(self.cY * Config.Playground.height / Config.Playground.cHeight)
        )
