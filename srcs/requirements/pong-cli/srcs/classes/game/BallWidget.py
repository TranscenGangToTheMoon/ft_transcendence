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
        self.offset = Offset(Config.Playground.width / 2 - 1, Config.Playground.height / 2 - 1)
        pass

    def render(self):
        # return "▄▄\n▀▀"
        return ""
