# Textual imports
from textual            import on
from textual.app        import ComposeResult
from textual.containers import Grid
from textual.screen     import ModalScreen
from textual.widgets    import Button, Label, Static

# Local imports
from classes.utils.config   import Config

class GameEnd(ModalScreen[str]):
    CSS_PATH = "styles/GameEnd.tcss"

    def __init__(self, reason: str, victory: bool):
        super().__init__()
        if (reason == Config.FinishReason.NORMAL_END):
            self.result = "You won" if victory else "You lost"
            self.styles.background = "blue 15%" if victory else "red 15%"
        else:
            self.result = f"The game did not end as expected\n{reason}"
            self.styles.background = "green 15%"

    @on(Button.Pressed, "#exit")
    def exit(self):
        self.app.exit()

    @on(Button.Pressed, "#mainMenu")
    def mainPage(self):
        self.dismiss("main")

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(f"{self.result}", id="reason"),
            Button("Main Menu", variant="primary", id="mainMenu"),
            Button("Exit", variant="error", id="exit"),
            id="dialog",
        )
