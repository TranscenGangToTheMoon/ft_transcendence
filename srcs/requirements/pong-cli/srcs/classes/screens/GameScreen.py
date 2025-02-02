# Python imports
import aiohttp
import asyncio
import socketio
import ssl
import time
from pynput import keyboard

# Textual imports
from textual            import on, work
from textual.app        import ComposeResult
from textual.geometry   import Offset
from textual.screen     import Screen
from textual.widgets    import Digits, Footer, Header, Label

# Local imports
from classes.game.BallWidget                    import Ball
from classes.game.PaddleWidget                  import Paddle
from classes.game.PlaygroundWidget              import Playground
from classes.modalScreens.CountdownModalScreen  import Countdown
from classes.modalScreens.GameEndModalScreen    import GameEnd
from classes.utils.config                       import Config
from classes.utils.user                         import User

class GamePage(Screen):
    SUB_TITLE = "Game Page"
    CSS_PATH = "styles/GamePage.tcss"
    BINDINGS = [
        ("^q", "exit", "Exit"),
        ("f", "forfeit", "Quit game")
    ]

    def __init__(self):
        super().__init__()
        self.playground = Playground()
        self.paddleLeft = Paddle("left")
        self.paddleRight = Paddle("right")
        self.ball = Ball()
        self.scoreLeft = Digits("0", id="scoreLeft")
        self.scoreRight = Digits("0", id="scoreRight")
        self.opponentLabel = Label(User.opponent, id="opponentLabel")
        self.aScore = 0
        self.bScore = 0

        self.lastFrame = 0
        self.countdownIsActive = False
        self.pressedKeys = set()
        self.listener = None
        self.gameStarted = False
        SSLContext = ssl.create_default_context()
        SSLContext.load_verify_locations(Config.SSL.CRT)
        SSLContext.check_hostname = False
        connector = aiohttp.TCPConnector(ssl=SSLContext)
        self.HTTPSession = aiohttp.ClientSession(connector=connector)
        self.sio = socketio.AsyncClient(
            http_session=self.HTTPSession,
            reconnection=False,
            # logger=True,
            # engineio_logger=True,
        )

    async def on_mount(self) -> None:
        Config.Console.reload()

        # Score handling
        self.scoreLeft.styles.offset = Offset(Config.Console.width // 4, 5)
        self.scoreRight.styles.offset = Offset(Config.Console.width // 4 * 3 - 4, 5)
        self.opponentLabel.styles.layer = "4"
        self.opponentLabel.styles.offset = Offset(
            self.playground.offset.x,
            self.playground.offset.y + Config.Playground.height + 1
        )

        # Key handling
        self.listener = keyboard.Listener(
            on_press=self.onPress,
            on_release=self.onRelease)
        self.listener.start()

        # Game handling
        await self.startSIOServer()
        self.gameLoop()

    def on_resize(self) -> None:
        Config.Console.reload()

        self.playground.styles.offset = Offset((Config.Console.width - Config.Playground.width) // 2, (Config.Console.height - Config.Playground.height) // 2)
        self.scoreLeft.styles.offset = Offset(Config.Console.width // 4, 5)
        self.scoreRight.styles.offset = Offset(Config.Console.width // 4 * 3 - 4, 5)
        self.opponentLabel.styles.offset = Offset(
            self.playground.offset.x,
            self.playground.offset.y + Config.Playground.height + 1
        )

    async def action_forfeit(self):
        while (self.countdownIsActive == True):
            await asyncio.sleep(1 / 10)
        self.dismiss()
        await self.sio.disconnect()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield self.scoreLeft
        yield self.scoreRight
        with self.playground:
            yield self.paddleLeft
            yield self.ball
            yield self.paddleRight
        yield self.opponentLabel
        yield Footer()

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
        while (not self.sio.connected or not self.gameStarted):
            await asyncio.sleep(0.1)

        while (self.sio.connected and self.gameStarted):
            if (self.lastFrame == 0):
                self.lastFrame = time.perf_counter()
                await asyncio.sleep(1 / Config.frameRate)
                continue
            dTime = time.perf_counter() - self.lastFrame
            if (self.countdownIsActive == True):
                await asyncio.sleep(1 / Config.frameRate)
                continue

            # Move right paddle
            if (keyboard.Key.up in self.pressedKeys and keyboard.Key.down in self.pressedKeys):
                if (self.paddleRight.direction != 0):
                    await self.sio.emit('stop_moving', {"position": self.paddleRight.cY})
            elif (keyboard.Key.up in self.pressedKeys):
                if (self.paddleRight.direction == 1):
                    await self.sio.emit('stop_moving', {"position": self.paddleRight.cY})
                if (self.paddleRight.direction != -1):
                    await self.sio.emit('move_up')
                self.paddleRight.moveUp(1 / dTime)
            elif (keyboard.Key.down in self.pressedKeys):
                if (self.paddleRight.direction == -1):
                    await self.sio.emit('stop_moving', {"position": self.paddleRight.cY})
                if self.paddleRight.direction != 1:
                    await self.sio.emit('move_down')
                self.paddleRight.moveDown(1 / dTime)
            elif (self.paddleRight.direction != 0):
                await self.sio.emit('stop_moving', {"position": self.paddleRight.cY})
                self.paddleRight.direction = 0

            # Move left paddle
            if (self.paddleLeft.direction == -1):
                self.paddleLeft.moveUp(1 / dTime)
            if (self.paddleLeft.direction == 1):
                self.paddleLeft.moveDown(1 / dTime)

            # Move ball
            self.ball.move(1 / dTime)

            # Check wall bounce
            if (self.ball.cY <= 0):
                self.ball.cdY *= -1
                self.ball.cY *= -1
            elif (self.ball.cY + Config.Ball.cSize > Config.Playground.cHeight):
                self.ball.cdY *= -1
                self.ball.cY -= self.ball.cY + Config.Ball.cSize - Config.Playground.cHeight

            elapsedTime = time.perf_counter() - self.lastFrame
            self.lastFrame = time.perf_counter()
            await asyncio.sleep(1 / (Config.frameRate - elapsedTime))

    async def startSIOServer(self):
        try:
            self.setHandler()
            await self.sio.connect(
                f"wss://{User.server}/",
                socketio_path="/ws/game/",
                transports=["websocket"],
                auth={
                    "id": User.id,
                    "token": User.accessToken
                }
            )
        except Exception as error:
            print(f"From socketio launching: {error}")
            self.dismiss()

    def setHandler(self):
        @self.sio.on('connect')
        async def connect():
            print("Connected to server!", flush=True)

        @self.sio.on('disconnect')
        async def disconnect():
            print("Disconnected from server event!", flush=True)
            if (User.inAGame):
                while (self.countdownIsActive == True):
                    await asyncio.sleep(1/10)
                await self.app.push_screen_wait(GameEnd(Config.FinishReason.SERVER_DISCONNECT, False))
            User.inAGame = False

        @self.sio.on('start_game')
        async def startGameAction():
            User.inAGame = True
            self.lastFrame = 0
            self.gameStarted = True

        @self.sio.on('start_countdown')
        async def startCountdownAction():
            self.countdownIsActive = True
            await self.app.push_screen_wait(Countdown())
            self.countdownIsActive = False

        @self.sio.on('game_state')
        async def gameStateAction(data):
            self.ball.cdX = data["speed_x"]
            self.ball.cdY = data["speed_y"]
            self.ball.moveTo(data["position_x"], data["position_y"])

        @self.sio.on('connect_error')
        async def connectErrorAction(data):
            print(f"Connect error received: {data}", flush=True)

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

        @self.sio.on('call_spectate')
        async def callSpectateAction(data):
            User.inAGame = False
            while (self.countdownIsActive == True):
                await asyncio.sleep(1/10)
            await self.app.push_screen_wait(GameEnd(Config.FinishReason.SPECTATE, False))
            await self.sio.disconnect() # maybe delete
            User.inAGame = False # maybe delete
            self.dismiss()

        @self.sio.on('game_over')
        async def gameOverAction(data):
            User.inAGame = False
            while (self.countdownIsActive == True):
                await asyncio.sleep(1/10)
            await self.app.push_screen_wait(GameEnd(data["reason"], data["winner"] == User.team))
            self.dismiss()

    async def on_unmount(self) -> None:
        self.listener.stop()
        await self.HTTPSession.close()
