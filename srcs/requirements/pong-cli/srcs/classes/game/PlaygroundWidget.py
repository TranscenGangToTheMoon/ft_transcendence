# Rich imports
from rich.console   import Console

# Textual imports
from textual.geometry   import Offset
from textual.widget     import Widget

# Local imports
from classes.utils.config   import Config


class Playground(Widget):
    def __init__(self):
        super().__init__()
        self.styles.width = Config.Playground.width
        self.styles.height = Config.Playground.height
        self.styles.layers = "1 2"

    def render(self):
        # return ""
        return "                                                         |\n" * Config.Playground.width
        # return ".*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.█.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.\n" * self.region.width

    def on_mount(self):
        console = Console()
        Config.Console.width = console.width
        Config.Console.height = console.height

        self.styles.offset = Offset((Config.Console.width - Config.Playground.width) // 2, (Config.Console.height - Config.Playground.height) // 2)
        self.styles.background = "blue"
        # self.styles.border = ("solid", "white")

    # def on_resize(self, event: events.Resize):
    #     pass
