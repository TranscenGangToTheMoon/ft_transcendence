# Textual imports
from textual.geometry   import Offset
from textual.widget     import Widget

# Local imports
from classes.utils.config   import Config

class Ball(Widget):
    def __init__(self):
        super().__init__()
        self.styles.layer = "3"
        self.styles.width = Config.Ball.width
        self.styles.height = Config.Ball.height
        self.styles.background = "white"
        self.cX = Config.Playground.cWidth / 2 - (Config.Ball.cSize / 2)
        self.cY = Config.Playground.cHeight / 2 - (Config.Ball.cSize / 2)
        self.cdX = 0
        self.cdY = 0
        self.offset = Offset(
            int(self.cX  * Config.Playground.width / Config.Playground.cWidth),
            int(self.cY * Config.Playground.height / Config.Playground.cHeight)
        )

    def render(self):
        return ""

    def move(self, dT: float):
        self.cX += self.cdX / dT
        self.cY += self.cdY / dT
        self.offset = Offset(
            int(self.cX  * Config.Playground.width / Config.Playground.cWidth),
            int(self.cY * Config.Playground.height / Config.Playground.cHeight)
        )

    def moveTo(self, cX: float, cY: float):
        self.cX = cX
        self.cY = cY
        self.offset = Offset(
            int(self.cX  * Config.Playground.width / Config.Playground.cWidth),
            int(self.cY * Config.Playground.height / Config.Playground.cHeight)
        )
