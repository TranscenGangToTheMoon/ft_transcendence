# Python imports
import asyncio
import threading
import time
import requests
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
from classes.utils.config           import Config, SSL_CRT, SSL_KEY
from classes.utils.user             import User

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
        self.listener = None
        self.connected = False
        httpSession = requests.Session()
        httpSession.verify = SSL_CRT
        httpSession.cert = (SSL_CRT, SSL_KEY)

        self.sio = socketio.Client(
            http_session=httpSession,
            # logger=True,
            # engineio_logger=True,
        )

        self.sio_lock = threading.Lock()
        self.gameStarted = False

    def on_mount(self):
        #key handling
        self.listener = keyboard.Listener(
            on_press=self.onPress,
            on_release=self.onRelease)
        self.listener.start()
        #game handling
        self.launchSocketIO()
        # self.gameLoop()
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
            self.dismiss()
            # self.app.exit() #to handle when voila
            # self.dismiss()

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

    @work
    async def gameLoop(self):
        while not self.connected or not self.gameStarted:
            pass
        print(f"Connected: {self.connected}, Game started: {self.gameStarted}")
        while self.connected and self.gameStarted:
            #Move right paddle
            if keyboard.Key.up in self.pressedKeys:
                if self.paddleRight.direction == 1:
                    self.sio.emit('stop_moving', {"position": self.paddleRight.cY})
                self.paddleRight.moveUp()
                self.sio.emit('move_up')
            elif keyboard.Key.down in self.pressedKeys:
                if self.paddleRight.direction == -1:
                    self.sio.emit('stop_moving', {"position": self.paddleRight.cY})
                self.paddleRight.moveDown()
                self.sio.emit('move_down')
            else:
                self.sio.emit('stop_moving', {"position": self.paddleRight.cY})
                self.paddleRight.direction = 0

            #Move left paddle
            if (self.paddleLeft.direction == -1):
                self.paddleLeft.moveUp()
            if (self.paddleLeft.direction == 1):
                self.paddleLeft.moveDown()
            await asyncio.sleep(1 / Config.frameRate)

    # def checkWallBounce(self):
    #     if (self.ball.offset.y <= 0):
    #         #mirror y position
    #         self.ball.dy *= -1
    #         print("hit upper wall")
    #     elif (self.ball.offset.y + Config.Ball.height > Config.Playground.height): #maybe -1
    #         #mirror y position
    #         self.ball.dy *= -1
    #         print("hit lower wall")

    def launchSocketIO(self):
        try:
            self.setHandler()
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
            self.connected = True
            print("Connected to server event!", flush=True)
            print(self.connected, flush=True)

        @self.sio.on('disconnect')
        def disconnect():
            self.connected = False
            # self.dismiss()
            print("Disconnected from server event!", flush=True)
            print(self.connected, flush=True)

        @self.sio.on('start_game')
        def start_game_action():
            self.gameStarted = True
            print("start_game_action", flush=True)
            print(self.connected, flush=True)

        @self.sio.on('start_countdown')
        def start_countdown_action():
            print("start_countdown_action", flush=True)
            print(self.connected, flush=True)

        @self.sio.on('game_state')
        def gameStateAction(data):
            self.ball.move(data["position_x"] / 7, data["position_y"] / 15)
            self.ball.dx = data["direction_x"] / 7
            self.ball.dy = data["direction_y"] / 15
            self.ball.speed = data["speed"]

        @self.sio.on('connect_error')
        def connectErrorAction(data):
            print(f"Connect error received: {data}", flush=True)
            print(self.connected, flush=True)

        @self.sio.on('move_up')
        def moveUpAction(data):
            print(f"move_up_action: {data}", flush=True)
            if (data["player"] != User.id):
                self.paddleLeft.direction = -1
            print(self.connected, flush=True)

        @self.sio.on('move_down')
        def moveDownAction(data):
            print(f"move_down_action: {data}", flush=True)
            if (data["player"] != User.id):
                self.paddleLeft.direction = 1
            print(self.connected, flush=True)

        @self.sio.on('stop_moving')
        def stopMovingAction(data):
            if (data["player"] == User.id):
                self.paddleRight.stopMoving(data["position"])
            else:
                self.paddleLeft.stopMoving(data["position"])

        @self.sio.on('score')
        def score_action(data):
            print(f"score_action: {data}", flush=True)
            print(self.connected, flush=True)

        @self.sio.on('game_over')
        def game_over_action(data):
            print(f"game_over_action: {data}", flush=True)
            print(self.connected, flush=True)

    def on_unmount(self) -> None:
        if (self.connected):
            self.sio.disconnect()
            print("Unmount disconnect the server!")
        self.connected = False
        self.listener.stop()
