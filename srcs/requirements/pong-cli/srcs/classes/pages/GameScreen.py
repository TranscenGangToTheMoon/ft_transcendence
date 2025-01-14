# Python imports
import asyncio
import ssl
import aiohttp
import socketio
from pynput import keyboard

# Rich imports
from rich.console   import Console

# Textual imports
from textual            import work
from textual.app        import ComposeResult
from textual.geometry   import Offset
from textual.screen     import Screen
from textual.widgets    import Button, Digits, Footer, Header

# Local imports
from classes.game.BallWidget                    import Ball
from classes.game.PaddleWidget                  import Paddle
from classes.game.PlaygroundWidget              import Playground
from classes.modalScreen.CountdownModalScreen   import Countdown
from classes.utils.config                       import Config, SSL_CRT
from classes.utils.user                         import User

class GamePage(Screen):
    SUB_TITLE = "Game Page"
    CSS_PATH = "styles/GamePage.tcss"

    def __init__(self):
        super().__init__()
        self.playground = Playground()
        self.paddleLeft = Paddle("left")
        self.paddleRight = Paddle("right")
        self.ball = Ball()
        self.scoreLeft = Digits("0", id="scoreLeft")
        self.scoreRight = Digits("0", id="scoreRight")
        self.aScore = 0
        self.bScore = 0

        self.styles.layers = "1 2"

        self.pressedKeys = set()
        self.listener = None
        self.connected = False
        self.gameStarted = False
        SSLContext = ssl.create_default_context()
        SSLContext.load_verify_locations(SSL_CRT)
        SSLContext.check_hostname = False
        connector = aiohttp.TCPConnector(ssl=SSLContext)
        self.HTTPSession = aiohttp.ClientSession(connector=connector)
        self.sio = socketio.AsyncClient(
            http_session=self.HTTPSession,
            # logger=True,
            # engineio_logger=True,
        )


    async def on_mount(self) -> None:
        console = Console()
        Config.Console.width = console.width
        Config.Console.height = console.height
        # Score board
        # self.scoreLeft.styles.border = ("solid", "white")
        self.scoreLeft.styles.layer = "1"
        self.scoreLeft.styles.width = 3
        self.scoreLeft.styles.offset = Offset(Config.Console.width // 4, 5)
        # self.scoreRight.styles.border = ("solid", "white")
        self.scoreRight.styles.layer = "2"
        self.scoreLeft.styles.offset = Offset(Config.Console.width // 4 * 3, 5)
        self.scoreRight.styles.width = 3

        # Key handling
        self.listener = keyboard.Listener(
            on_press=self.onPress,
            on_release=self.onRelease)
        self.listener.start()

        # Game handling
        await self.launchSocketIO()
        self.gameLoop()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield self.scoreLeft
        yield self.scoreRight
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
        print(f"Width: {self.region.width}")
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
            elif (keyboard.Key.down in self.pressedKeys):
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
        async def startGameAction():
            self.gameStarted = True
            print("start_game_action", flush=True)
            print(self.connected, flush=True)

        @self.sio.on('start_countdown')
        async def start_countdown_action():
            print("start_countdown_action", flush=True)
            print(self.connected, flush=True)

        @self.sio.on('game_state')
        async def gameStateAction(data):
            self.ball.move(data["position_x"], data["position_y"])

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
        async def scoreAction(data):
            print(f"Score action event ====: {data}", flush=True)
            self.aScore = data["team_a"]
            self.bScore = data["team_b"]
            if (User.team == "a"):
                self.query_one("#scoreLeft").update(str(self.bScore))
                self.query_one("#scoreRight").update(str(self.aScore))
            else:
                self.query_one("#scoreLeft").update(str(self.aScore))
                self.query_one("#scoreRight").update(str(self.bScore))
            self.paddleLeft.reset()
            self.paddleRight.reset()
            print(self.connected, flush=True)

        @self.sio.on('game_over')
        async def game_over_action(data):
            print(f"game_over_action: {data}", flush=True)
            await self.sio.disconnect()
            print(self.connected, flush=True)

    async def on_unmount(self) -> None:
        print("Unmounting GamePage")
        if (self.connected):
            await self.sio.disconnect()
            print("Unmount disconnect the server!")
        self.connected = False
        self.listener.stop()
        await self.HTTPSession.close()
