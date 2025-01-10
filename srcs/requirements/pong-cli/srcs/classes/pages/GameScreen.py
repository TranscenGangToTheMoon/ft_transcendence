# Python imports
import asyncio
import ssl
import threading
import time

import aiohttp
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

        # ssl_context = ssl.create_default_context()
        # ssl_context.load_cert_chain(SSL_CRT)
        # connector = aiohttp.TCPConnector(ssl=ssl_context)
        # http_session = aiohttp.ClientSession(connector=connector)
        self.sio = socketio.AsyncClient(
            # http_session=http_session,
            ssl_verify=False,
            # logger=True,
            # engineio_logger=True,
        )
        self.gameStarted = False

    async def on_mount(self) -> None:
        # Key handling
        self.listener = keyboard.Listener(
            on_press=self.onPress,
            on_release=self.onRelease)
        self.listener.start()

        # Game handling
        await self.launchSocketIO()
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
        if event.button.id == "exitAction":
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

    @work
    async def gameLoop(self):
        while (not self.connected or not self.gameStarted):
            await asyncio.sleep(0.1)
        print(f"Connected: {self.connected}, Game started: {self.gameStarted}")
        while (self.connected and self.gameStarted):
            # Move right paddle
            if (keyboard.Key.up in self.pressedKeys):
                if self.paddleRight.direction == 1:
                    await self.sio.emit('stop_moving', {"position": self.paddleRight.cY})
                self.paddleRight.moveUp()
                await self.sio.emit('move_up')
            elif keyboard.Key.down in self.pressedKeys:
                if self.paddleRight.direction == -1:
                    await self.sio.emit('stop_moving', {"position": self.paddleRight.cY})
                self.paddleRight.moveDown()
                await self.sio.emit('move_down')
            else:
                await self.sio.emit('stop_moving', {"position": self.paddleRight.cY})
                self.paddleRight.direction = 0

            # Move left paddle
            if (self.paddleLeft.direction == -1):
                self.paddleLeft.moveUp()
            if (self.paddleLeft.direction == 1):
                self.paddleLeft.moveDown()

            await asyncio.sleep(1 / Config.frameRate)

    async def launchSocketIO(self):
        try:
            self.setHandler()
            await self.sio.connect(
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
        async def connect():
            self.connected = True
            print("Connected to server event!", flush=True)
            print(self.connected, flush=True)

        @self.sio.on('disconnect')
        async def disconnect():
            self.connected = False
            print("Disconnected from server event!", flush=True)
            print(self.connected, flush=True)

        @self.sio.on('start_game')
        async def start_game_action():
            self.gameStarted = True
            print("start_game_action", flush=True)
            print(self.connected, flush=True)

        @self.sio.on('start_countdown')
        async def start_countdown_action():
            print("start_countdown_action", flush=True)
            print(self.connected, flush=True)

        @self.sio.on('game_state')
        async def gameStateAction(data):
            self.ball.move(data["position_x"] / 7, data["position_y"] / 15)
            self.ball.dx = data["direction_x"] / 7
            self.ball.dy = data["direction_y"] / 15
            self.ball.speed = data["speed"]

        @self.sio.on('connect_error')
        async def connectErrorAction(data):
            print(f"Connect error received: {data}", flush=True)
            print(self.connected, flush=True)

        @self.sio.on('move_up')
        async def moveUpAction(data):
            if (data["player"] != User.id):
                self.paddleLeft.direction = -1

        @self.sio.on('move_down')
        async def moveDownAction(data):
            if (data["player"] != User.id):
                self.paddleLeft.direction = 1

        @self.sio.on('stop_moving')
        async def stopMovingAction(data):
            if (data["player"] == User.id):
                self.paddleRight.stopMoving(data["position"])
            else:
                self.paddleLeft.stopMoving(data["position"])

        @self.sio.on('score')
        async def score_action(data):
            print(f"score_action: {data}", flush=True)
            print(self.connected, flush=True)

        @self.sio.on('game_over')
        async def game_over_action(data):
            print(f"game_over_action: {data}", flush=True)
            print(self.connected, flush=True)

    async def on_unmount(self) -> None:
        print("Unmount GamePage")
        if (self.connected):
            await self.sio.disconnect()
            print("Unmount disconnect the server!")
        self.connected = False
        self.listener.stop()
