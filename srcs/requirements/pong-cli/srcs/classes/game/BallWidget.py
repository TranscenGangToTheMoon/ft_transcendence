# Python imports
import math
import random

# Textual imports
from textual.geometry   import Offset
from textual.widget     import Widget

# Local imports
from classes.utils.config   import Config

def get_random_direction():
    random_angle = random.random() * 2 * math.pi
    while abs(math.cos(random_angle)) < math.cos(math.pi / 3):
        random_angle = random.random() * 2 * math.pi
    return math.cos(random_angle), math.sin(random_angle)

class Ball(Widget):
    def __init__(self):
        super().__init__()
        self.styles.layer = "3"
        self.styles.width = Config.Ball.width
        self.styles.height = Config.Ball.height
        self.styles.background = "white"
        self.cX = Config.Playground.cWidth / 2 - (Config.Ball.cWidth / 2)
        self.cY = Config.Playground.cHeight / 2 - (Config.Ball.cHeight / 2)
        self.offset = Offset(
            int(self.cX  * Config.Playground.width / Config.Playground.cWidth),
            int(self.cY * Config.Playground.height / Config.Playground.cHeight)
        )

    def render(self):
        # return "▄▄\n▀▀"
        return ""

    def move(self, cX: float, cY: float):
        self.cX = cX
        self.cY = cY
        self.offset = Offset(
            int(self.cX  * Config.Playground.width / Config.Playground.cWidth),
            int(self.cY * Config.Playground.height / Config.Playground.cHeight)
        )
        # print(f"{self.offset} += {Offset(self.dx, self.dy)}")
