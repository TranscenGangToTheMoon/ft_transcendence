# Python imports
import asyncio

# Textual imports
from textual            import work
from textual.app        import ComposeResult
from textual.widgets    import Digits
from textual.screen     import ModalScreen

class Countdown(ModalScreen):
    CSS_PATH = "styles/CountdownModalScreen.tcss"

    def __init__(self):
        super().__init__()
        self.countdown = 3
        self.digits = Digits(str(self.countdown), id="countdown")
        self.start()

    def compose(self) -> ComposeResult:
        yield self.digits

    @work
    async def start(self):
        while self.countdown > 0:
            await asyncio.sleep(2/3)
            self.countdown -= 1
            self.query_one("#countdown").update(str(self.countdown))
        self.dismiss()