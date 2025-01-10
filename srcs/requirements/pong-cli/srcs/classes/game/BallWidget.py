# Python imports
import math
import random
from collections import namedtuple
from typing import NamedTuple

# Textual imports
from textual.geometry   import Offset, Region
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
        self.cX = int(Config.Playground.cWidth / 2 - (Config.Ball.cWidth / 2))
        self.cY = int(Config.Playground.cHeight / 2 - (Config.Ball.cHeight / 2))
        self.offset = Offset(self.cX  * Config.Playground.width / Config.Playground.cWidth,
                             self.cY * Config.Playground.height / Config.Playground.cHeight)
        self.speed = 0
        self.cdX = 0
        self.cdY = 0
        self.dx = 0
        self.dy = 0

    def render(self):
        # return "▄▄\n▀▀"
        return ""

    def move(self, x = None, y = None):
        if (not x or not y):
            self.offset += Offset(self.dx, self.dy)
        elif (x and y):
            self.offset = Offset(x, y)
        # print(f"{self.offset} += {Offset(self.dx, self.dy)}")
