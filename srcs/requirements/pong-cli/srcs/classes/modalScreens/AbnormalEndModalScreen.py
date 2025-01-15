# Python imports

# Textual imports
from textual.app        import ComposeResult
from textual.widgets    import Static
from textual.screen     import ModalScreen

# Local imports
from classes.utils.config   import Config


class AbnormalEnd(ModalScreen):
    # CSS_PATH = "styles/AbnormalEnd.tcss"
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
    def __init__(self, finishReason: str):
        super().__init__()
        print(f"End because {finishReason}")
        if (finishReason == Config.FinishReason.PLAYER_DISCONNECT):
            self.result = Static(Config.FinishReason.PLAYER_DISCONNECT)
        elif (finishReason == Config.FinishReason.PLAYER_NOT_CONNECTED):
            self.result = Static(Config.FinishReason.PLAYER_NOT_CONNECTED)
        elif (finishReason == Config.FinishReason.PLAYERS_TIMEOUT):
            self.result = Static(Config.FinishReason.PLAYERS_TIMEOUT)
    def compose(self) -> ComposeResult:
        yield self.result

