# Python imports
import asyncio
import threading
import time

from pynput import keyboard

# Textual imports
from textual            import work
from textual.app        import ComposeResult
from textual.geometry import Offset
from textual.screen     import Screen
from textual.widgets    import Header, Button, Footer

# Local imports
from classes.game.BallWidget        import Ball
from classes.game.PaddleWidget      import Paddle
from classes.game.PlaygroundWidget  import Playground
from classes.utils.config           import Config



class GamePage(Screen):
    SUB_TITLE = "Game Page"
    CSS_PATH = "styles/GamePage.tcss"
    def __init__(self):
        super().__init__()
        self.playground = Playground()
        self.paddleLeft = Paddle("left")
        self.paddleRight = Paddle("right")
        self.ball = Ball()
        self.pressedKeys = set()
        self.running = True
        self.key_thread = threading.Thread(target=self.checkKeys)
        self.listener = None

    def on_mount(self):
        #key handling
        self.key_thread.daemon = True
        self.key_thread.start()
        self.listener = keyboard.Listener(
            on_press=self.onPress,
            on_release=self.onRelease)
        self.listener.start()
        #game handling
        self.gameLoop()

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
            self.running = False
            self.dismiss()

    def onPress(self, key):
        try:
            self.pressedKeys.add(key.char)
        except (AttributeError, TypeError):
            self.pressedKeys.add(key)

    def onRelease(self, key):
        try:
            self.pressedKeys.remove(key.char)
        except (KeyError, AttributeError, TypeError):
            try:
                self.pressedKeys.remove(key)
            except KeyError:
                pass

    def checkKeys(self):
        while self.running:
            if 'w' in self.pressedKeys:
                self.paddleLeft.moveUp()
            if 's' in self.pressedKeys:
                self.paddleLeft.moveDown()
            if keyboard.Key.up in self.pressedKeys:
                self.paddleRight.moveUp()
            if keyboard.Key.down in self.pressedKeys:
                self.paddleRight.moveDown()
            time.sleep(1/60)

    def checkWallBounce(self):
        if (self.ball.offset.y <= 0):
            #mirror y position
            self.ball.dy *= -1
            print("hit upper wall")
        elif (self.ball.offset.y + Config.Ball.height > Config.Playground.height): #maybe -1
            #mirror y position
            self.ball.dy *= -1
            print("hit lower wall")

    # def checkPaddleBounce(self, paddle: Paddle):
    #     if ()
    #     #if (one of corner of the ball is inside the paddle)
    #         # bounce
    #     pass
    #     # if (self.paddleLeft.reg)

    @work
    async def gameLoop(self):
        # pass
        while self.running:
            # print("Loop")
            self.ball.move()
            self.checkWallBounce()
            self.checkPaddleBounce(self.paddleLeft)
            self.checkPaddleBounce(self.paddleRight)
            await asyncio.sleep(1/60)
            print(f"{self.ball.offset}")

    @work
    async def eventFromServer(self):
        pass

    def on_unmount(self) -> None:
        self.running = False
        self.listener.stop()