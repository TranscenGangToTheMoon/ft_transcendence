# Python imports
import asyncio
import threading
import time

import socketio
from pynput import keyboard

# Textual imports
from textual            import work
from textual.app        import ComposeResult
from textual.screen     import Screen
from textual.widgets    import Header, Button, Footer

# Local imports
from classes.game.BallWidget        import Ball
from classes.game.PaddleWidget      import Paddle
from classes.game.PlaygroundWidget  import Playground
from classes.utils.config           import Config
from classes.utils.user             import User
from classes.utils.config           import SSL_CRT


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
        self.sio = socketio.Client(ssl_verify=False)

    def on_mount(self):
        #key handling
        self.key_thread.daemon = True
        self.key_thread.start()
        self.listener = keyboard.Listener(
            on_press=self.onPress,
            on_release=self.onRelease)
        self.listener.start()
        #game handling
        self.eventFromServer()
        self.setHandler()
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
            # if 'w' in self.pressedKeys:
            #     self.paddleLeft.moveUp()
            # if 's' in self.pressedKeys:
            #     self.paddleLeft.moveDown()
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
            # self.ball.move()
            self.checkWallBounce()
            # self.checkPaddleBounce(self.paddleLeft)
            # self.checkPaddleBounce(self.paddleRight)
            await asyncio.sleep(1/60)
            # print(f"{self.ball.offset}")

    def eventFromServer(self):
        try:
            self.sio.connect(
                "wss://localhost:4443/",
                socketio_path="/ws/game/",
                transports=["websocket"],
                auth={
                    "id": User.id,
                    "token": User.accessToken
                }
            )
            print("Connected to server!")
        except Exception as error:
            print(f"From event: {error}")

    def setHandler(self):
        @self.sio.on('connect')
        def connect():
            print("Connected to server event!")
            print(self.running)

        @self.sio.on('start_game')
        def start_game_action():
            print("start_game_action")
            print(self.running)

        @self.sio.on('start_countdown')
        def start_countdown_action():
            print("start_countdown_action")
            print(self.running)

        @self.sio.on('game_state')
        def game_state_action(data):
            print(f"game_state_action: {data}")
            print(self.running)

        @self.sio.on('connect_error')
        def connect_error_action():
            print("connect_error_action")
            print(self.running)

        @self.sio.on('move_up')
        def move_up_action(data):
            print(f"move_up_action: {data}")
            print(self.running)

        @self.sio.on('move_down')
        def move_down_action(data):
            print(f"move_down_action: {data}")
            print(self.running)

        @self.sio.on('stop_moving')
        def stop_moving_action(data):
            print(f"stop_moving_action: {data}")
            print(self.running)

        @self.sio.on('score')
        def score_action(data):
            print(f"score_action: {data}")
            print(self.running)

        @self.sio.on('game_over')
        def game_over_action(data):
            print(f"game_over_action: {data}")
            print(self.running)

    def on_unmount(self) -> None:
        self.running = False
        self.listener.stop()

    # socket.on('connect', connect_action)
    # socket.on('start_game', start_game_action)
    # socket.on('start_countdown', start_countdown_action)
    # socket.on('game_state', game_state_action)
    # socket.on('connect_error', connect_error_action)
    # socket.on('move_up', move_up_action)
    # socket.on('move_down', move_down_action)
    # socket.on('stop_moving', stop_moving_action)
    # socket.on('score', score_action)
    # socket.on('game_over', game_over_action)