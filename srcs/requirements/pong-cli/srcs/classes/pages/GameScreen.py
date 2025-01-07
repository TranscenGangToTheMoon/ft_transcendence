# Python imports
import threading
import time

from pynput import keyboard

# Textual imports
from textual.app import ComposeResult
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
        self.pressed_keys = set()
        self.running = True
        self.key_thread = threading.Thread(target=self.check_keys)
        self.listener = None

    def on_mount(self):
        self.key_thread.daemon = True
        self.key_thread.start()

        # Configuration des listeners
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()

    def compose(self) -> ComposeResult:
        yield Header()
        with self.playground:
            yield self.paddleLeft
            yield self.ball
            yield self.paddleRight
        yield Button("Exit Button", id="exitAction")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if (event.button.id == "exitAction"):
            self.app.exit() #to handle when voila
            self.dismiss()

    def on_press(self, key):
        try:
            self.pressed_keys.add(key.char)
        except (AttributeError, TypeError):
            self.pressed_keys.add(key)

    def on_release(self, key):
        try:
            self.pressed_keys.remove(key.char)
        except (KeyError, AttributeError, TypeError):
            try:
                self.pressed_keys.remove(key)
            except KeyError:
                pass

    def check_keys(self):
        while self.running:
            if 'w' in self.pressed_keys:
                self.paddleLeft.moveUp()
            if 's' in self.pressed_keys:
                self.paddleLeft.moveDown()
            if keyboard.Key.up in self.pressed_keys:
                self.paddleRight.moveUp()
            if keyboard.Key.down in self.pressed_keys:
                self.paddleRight.moveDown()
            time.sleep(1/60)

    def on_unmount(self) -> None:
        self.running = False
        self.listener.stop()