# Rich imports
from rich.console   import Console

class Config:
    configJson = {}
    frameRate: int = 60
    errorCodes = {
        "not_authenticated": "Missing token",
        "incorrect_password": "Password incorrect",
        "user_not_found": "Unknown token",
        "authentication_failed": "Authentication failed",
        "sse_connection_required": "SSE connexion required",
        "password_confirmation_required": "Password confirmation required",
        "token_not_valid": "Invalid token",
        None: "Unknown error code"
    }

    @classmethod
    def load(cls, configJson = None):
        if (configJson is not None and configJson != {}):
            cls.configJson = configJson
        else:
            print("Invalid configuration file, using basic configuration.")
            cls.configJson = {}
        Config.Playground.load()
        Config.Paddle.load()
        Config.Ball.load()

    @classmethod
    def __str__(cls):
        return (
            f"frameRate:........... {cls.frameRate}\n"
            f"Cell.width:.......... {cls.Cell.width}\n"
            f"Cell.height:......... {cls.Cell.height}\n"
            f"Console.width:....... {cls.Console.width}\n"
            f"Console.height:...... {cls.Console.height}\n"
            f"Playground.cWidth:... {cls.Playground.cWidth}\n"
            f"Playground.cHeight:.. {cls.Playground.cHeight}\n"
            f"Playground.width:.... {cls.Playground.width}\n"
            f"Playground.height:... {cls.Playground.height}\n"
            f"Paddle.cGap:......... {cls.Paddle.cGap}\n"
            f"Paddle.cWidth:....... {cls.Paddle.cWidth}\n"
            f"Paddle.cHeight:...... {cls.Paddle.cHeight}\n"
            f"Paddle.cSpeed:....... {cls.Paddle.cSpeed}\n"
            f"Paddle.gap:.......... {cls.Paddle.gap}\n"
            f"Paddle.width:........ {cls.Paddle.width}\n"
            f"Paddle.height:....... {cls.Paddle.height}\n"
            f"Paddle.speed:........ {cls.Paddle.speed}\n"
            f"Ball.cSize:.......... {cls.Ball.cSize}\n"
            f"Ball.width:.......... {cls.Ball.width}\n"
            f"Ball.height:......... {cls.Ball.height}\n"
        )

    @classmethod
    def get(cls, *keys, default: int | None = None):
        value = cls.configJson
        for key in keys:
            value = value.get(key, {})
        return (value if value != {} else default)

    class Cell:
        width: int = 7
        height: int = 15

    class Console:
        width: int = 0
        height: int = 0

        @classmethod
        def reload(cls):
            console = Console()

            cls.width = console.width
            cls.height = console.height

    class Playground:
        cWidth: int = 1000
        cHeight: int = 600
        width: int = 142
        height: int = 40

        @classmethod
        def load(cls):
            if (Config.configJson != {}):
                cls.cWidth = Config.get("canvas", "normal", "width", default=1000)
                cls.cHeight = Config.get("canvas", "normal", "height", default=600)
                cls.width = int(cls.cWidth / Config.Cell.width)
                cls.height = int(cls.cHeight / Config.Cell.height)

    class Paddle:
        cGap: int = 100
        cWidth: int = 30
        cHeight: int = 200
        cSpeed: int = 500
        gap: int = 14
        width: int = 4
        height: int = 13
        speed: int = 33

        @classmethod
        def load(cls):
            if (Config.configJson != {}):
                cls.cGap = Config.get("paddle", "normal", "ledgeOffset", default=100)
                cls.cWidth = Config.get("paddle", "normal", "width", default=30)
                cls.cHeight = Config.get("paddle", "normal", "height", default=200)
                cls.cSpeed = Config.get("paddle", "normal", "speed", default=500)
                cls.gap = int(cls.cGap / Config.Cell.width)
                cls.width = int(cls.cWidth / Config.Cell.width)
                cls.height = int(cls.cHeight / Config.Cell.height)
                cls.speed = int(cls.cSpeed / Config.Cell.height)

    class Ball:
        cSize: int = 20
        width: int = 4
        height: int = 2

        @classmethod
        def load(cls):
            if (Config.configJson != {}):
                cls.cSize = Config.get("ball", "size", default=20)
                cls.width = 4
                cls.height = 2

    class FinishReason:
        NORMAL_END = 'normal-end'
        PLAYER_DISCONNECT = 'player-disconnect'
        PLAYER_NOT_CONNECTED = 'player-not-connected'
        PLAYERS_TIMEOUT = 'players-timeout'
        GAME_NOT_PLAYED = 'game-not-played'
        SPECTATE = 'spectate'
        SERVER_DISCONNECT = 'server-disconnect'

    class SSL:
        CRT = "ft_transcendence.crt"
