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
        self.offset = Offset((Config.Playground.width - Config.Ball.width) / 2, (Config.Playground.height - Config.Ball.height) / 2)
        # self.realOffset = namedtuple("RealOffset", ["x", "y"])(*self.offset)
        self.speed = Config.Ball.speed
        self.angle = self.getRandomAngle()
        self.dx = self.getRandomX() * self.speed
        self.dy = self.getRandomY() * self.speed

    def render(self):
        # return "▄▄\n▀▀"
        return ""

    def move(self, x = None, y = None):
        if (not x or not y):
            self.offset += Offset(self.dx, self.dy)
        elif (x and y):
            self.offset = Offset(x, y)
        # print(f"{self.offset} += {Offset(self.dx, self.dy)}")

    def getRandomAngle(self):
        randomAngle = random.random() * 2 * math.pi
        while abs(math.cos(randomAngle)) < math.cos(math.pi / 3):
            randomAngle = random.random() * 2 * math.pi
        return (randomAngle)

    def getRandomX(self):
        return (math.cos(self.angle)) #convert

    def getRandomY(self):
        return (math.sin(self.angle)) #convert