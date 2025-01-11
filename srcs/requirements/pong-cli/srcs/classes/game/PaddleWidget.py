# Python imports


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
        self.styles.background = "white"
        if side == "left":
            self.styles.layer = "1"

            self.cX = Config.Paddle.cGap
            self.offset = Offset(self.cX * Config.Playground.width / Config.Playground.cWidth, self.cY * Config.Playground.height / Config.Playground.cHeight)
        elif side == "right":
            self.styles.layer = "2"

            self.cX = Config.Playground.cWidth - Config.Paddle.cGap - Config.Paddle.cWidth
            self.offset = Offset(self.cX * Config.Playground.width / Config.Playground.cWidth, self.cY * Config.Playground.height / Config.Playground.cHeight)

    def render(self):
        return " " * Config.Paddle.height * Config.Paddle.width
        # return "█" * Config.Paddle.height * Config.Paddle.width

    def reset(self):
        self.cY = (Config.Playground.cHeight - Config.Paddle.cHeight) // 2
        self.offset = Offset(self.offset.x, self.cY * Config.Playground.height / Config.Playground.cHeight)

    def moveUp(self):
        self.direction = -1
        if self.cY - Config.Paddle.cSpeed / Config.frameRate > 0:
            self.cY -= Config.Paddle.cSpeed / Config.frameRate
        else:
            self.cY = 0
        self.offset = Offset(self.offset.x, round(self.cY * Config.Playground.height / Config.Playground.cHeight))

    def moveDown(self):
        self.direction = 1
        if self.cY + Config.Paddle.cSpeed / Config.frameRate < Config.Playground.cHeight - Config.Paddle.cHeight:
            self.cY += Config.Paddle.cSpeed / Config.frameRate
        else:
            self.cY = Config.Playground.cHeight - Config.Paddle.cHeight
        self.offset = Offset(self.offset.x, round(self.cY * Config.Playground.height / Config.Playground.cHeight))

    def stopMoving(self, cY: float):
        self.direction = 0
        self.cY = cY
        self.offset = Offset(self.offset.x, round(self.cY * Config.Playground.height / Config.Playground.cHeight))
