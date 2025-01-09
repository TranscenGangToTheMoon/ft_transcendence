class Position:
    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y

    def invert(self, canvas: Position):
        return Position(-self.x + canvas.x, self.y)
