# Python imports
import json
import re
import httpx

# Textual imports
from textual        import work, log
from textual.app    import App
from textual.worker import Worker

# Local imports
from classes.pages.GameScreen   import GamePage
from classes.utils.user         import User


class PongCLI(App):
    SCREENS = {
        # "loginPage": LoginPage,
    }

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self) -> None:
        super().__init__()
        self.regex = re.compile(r'event: ([a-z\-]+)\ndata: (.+)\n\n')
        self.connected = False

    @property
    def isConnected(self):
        return (self.connected)

    def on_mount(self) -> None:
        self.push_screen(GamePage())
        # self.push_screen(LoginPage())

    @work(exclusive=True)
    async def startSSE(self):
        log("Start SSE")
        if (not self.isConnected):
            self.connected = True
            async with httpx.AsyncClient(verify=User.SSLCertificate) as client:
                headers = {
                    'Content-Type': 'text/event-stream',
                    'Authorization': f'Bearer {User.accessToken}',
                }

                try:
                    async with client.stream('GET', f"{User.server}/sse/users/", headers=headers) as response:
                        if (response.status_code >= 400):
                            raise (Exception(f"({response.status_code}) SSE connection prout! {response.text}"))

                        async for line in response.aiter_text():
                            # if (self.is_cancelled):
                            #     break
                            # log("Prout")
                            try:
                                events = self.regex.findall(line)
                                for event, data in events:
                                    dataJson = None
                                    if (event == "game-start"):# game start
                                        dataJson = json.loads(data)
                                        log(f"{dataJson}")
                                        await self.push_screen(GamePage()) #maybe it's a solution
                                    elif (event != "game-start" and event != "ping"):
                                        log(f"{event}: {dataJson}")
                            except (IndexError, ValueError) as error:
                                continue
                finally:
                    self.connected = False

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        self.log(event)
    # def compose(self) -> ComposeResult:
    #     yield LoginPage(User)
    #
    # def changePage(self, page):
    #     match page:
    #         case Page.LoginPage:
    #             yield LoginPage(self.user)
    #         case Page.MainPage:
    #             yield Static("MainPage")
    #         case Page.GamePage:
    #             yield Static("GamePage")
