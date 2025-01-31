# Textual imports
from textual            import on
from textual.app        import ComposeResult
from textual.containers import Grid
from textual.screen     import ModalScreen
from textual.widgets    import Button, Label, Static

# Local imports
from classes.utils.config   import Config

class GameEnd(ModalScreen):
    CSS_PATH = "styles/GameEnd.tcss"

    def __init__(self, reason: str, victory: bool):
        super().__init__()
        if (reason == Config.FinishReason.SPECTATE):
            self.result = "Spectate event"
            self.styles.background = "green 15%"
        elif (reason == Config.FinishReason.CONNECTION_ERROR):
            self.result = "Connection error"
            self.styles.background = "red 50%"
        elif (reason == Config.FinishReason.NORMAL_END):
            self.result = "You win" if victory else "You lose"
            self.styles.background = "blue 15%" if victory else "red 15%"
        else:
            self.result = f"The game did not end as expected\n{reason}"
            self.styles.background = "purple 15%"

    @on(Button.Pressed, "#exit")
    def exit(self):
        self.app.exit()

    @on(Button.Pressed, "#mainMenu")
    def mainPage(self):
        self.dismiss()

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(f"{self.result}", id="reason"),
            Button("Main Menu", variant="primary", id="mainMenu"),
            Button("Exit", variant="error", id="exit"),
            id="dialog",
        )
