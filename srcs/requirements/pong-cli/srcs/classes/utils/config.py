class Config:
    class Console:
        width = 0
        height = 0
    class Playground:
        cWidth = 800
        cHeight = 600
        width = 114
        height = 40
    class Paddle:
        cGap = 100
        cWidth = 30
        cHeight = 200
        cSpeed = 500
        gap = 14
        width = 4
        height = 13
        speed = 33
    class Ball:
        cWidth = 20
        cHeight = 20
        width = 4
        height = 2
    class FinishReason:
        NORMAL_END = 'The game is over'
        PLAYER_DISCONNECT = 'A player has disconnected'
        PLAYER_NOT_CONNECTED = 'Not all players are connected'
        PLAYERS_TIMEOUT = 'Players have timed out'
    class Cell:
        width = 7
        height = 15
    class SSL:
        CRT = "ft_transcendence.crt"
        KEY = "ft_transcendence.key"
    frameRate = 60
