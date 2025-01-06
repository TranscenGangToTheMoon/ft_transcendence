# Textual imports
from textual import events
from textual.app        import ComposeResult
from textual.screen     import Screen
from textual.widgets    import Header, Button, Footer

# Local imports
from classes.game.PaddleWidget      import Paddle
from classes.game.PlaygroundWidget  import Playground
from classes.game.BallWidget        import Ball


class GamePage(Screen):
    SUB_TITLE = "Game Page"
    CSS_PATH = "styles/GamePage.tcss"

    def __init__(self):
        super().__init__()
        self.paddleLeft = Paddle("left")
        self.paddleRight = Paddle("right")
        self.ball = Ball()
        self.playground = Playground()
        self.keys_pressed = set()

    def compose(self) -> ComposeResult:
        # self.set_interval(1/20, self.updateMouvements)
        yield Header()
        with self.playground:
            yield self.paddleLeft
            yield self.ball
            yield self.paddleRight
        yield Button("Exit Button", id="exitAction")
        yield Footer()

    def on_mount(self) -> None:
        self.keys_pressed = set()

    def updateMouvements(self) -> None:
        if "w" in self.keys_pressed:
            self.paddleLeft.moveUp()
            # self.keys_pressed.remove("w")
        if "s" in self.keys_pressed:
            self.paddleLeft.moveDown()
#             self.keys_pressed.remove("s")
        if "up" in self.keys_pressed:
            self.paddleRight.moveUp()
#             self.keys_pressed.remove("up")
        if "down" in self.keys_pressed:
            self.paddleRight.moveDown()
#             self.keys_pressed.remove("down")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if (event.button.id == "exitAction"):
            self.dismiss()

    # def on_event(self, event: Event) -> None:
    def on_key(self, event) -> None: #key repeat for continuous press
        # self.keys_pressed.add(str(event.key))
        if event.key == "w":
            self.paddleLeft.moveUp()
        if event.key == "s":
            self.paddleLeft.moveDown()
        if event.key == "up":
            self.paddleRight.moveUp()
        if event.key == "down":
            self.paddleRight.moveDown()

    def on_key_up(self, event) -> None:
        pass