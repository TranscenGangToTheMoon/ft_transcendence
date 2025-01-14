# Python imports
import asyncio

# Textual imports
from textual            import work
from textual.app        import ComposeResult
from textual.widgets    import Digits
from textual.screen     import ModalScreen

class Countdown(ModalScreen):
    DEFAULT_CSS = """
        Countdown {
            align: center middle;
            background: black 0%;
        }
    """
    def __init__(self):
        super().__init__()
        self.countdown = 3
    #     # self.styles.align = ("center", "middle")
    #     # self.styles.width = "auto"
    #     # self.styles.height = "auto"
    #     # self.styles.background = "blue 12%"
    #     # self.styles.border = ("round", "white")
    #
        self.digits = Digits(str(self.countdown), id="countdown")
        self.digits.styles.width = 10
        self.digits.styles.height = "auto"
        self.digits.styles.content_align = ("center", "middle")
        self.digits.styles.border = ("round", "white")
        self.digits.styles.background = "gray"
        self.digits.styles.padding = (1, 2)
        self.start()
    #
    def compose(self) -> ComposeResult:
        yield self.digits

    @work
    async def start(self):
        while self.countdown > 0:
            await asyncio.sleep(2/3)
            self.countdown -= 1
            print(f"Countdown: {self.countdown}")
            self.query_one("#countdown").update(str(self.countdown))
        self.dismiss()