# Python imports

# Textual imports
from textual.app        import ComposeResult
from textual.widgets    import Static
from textual.screen     import ModalScreen

class GameOver(ModalScreen):
    # CSS_PATH = "styles/GameOverModalScreen.tcss"
    DEFAULT_CSS = """
        GameOver {
            align: center middle;
            background: red 15%;
        }
        Static {
            align: center middle;
            width: auto;
        }
    """
    def __init__(self, victory: bool):
        super().__init__()
        if (victory):
            self.styles.background = "blue 15%"
            self.result = Static("Victory")
        else:
            self.styles.background = "red 15%"
            self.result = Static("Defeat")

    def compose(self) -> ComposeResult:
        yield self.result

