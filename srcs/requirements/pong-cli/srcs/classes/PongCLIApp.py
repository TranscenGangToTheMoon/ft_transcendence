# Python imports
import httpx
import json
import re
import ssl

# Textual imports
from textual        import work
from textual.app    import App
from textual.worker import Worker

# Local imports
from classes.screens.GameScreen     import GamePage
from classes.screens.LoginScreen    import LoginPage
from classes.utils.config           import Config
from classes.utils.user             import User

class PongCLI(App):
    SCREENS = {}
    BINDINGS = [("^q", "exit", "Exit"), ]

    def __init__(self) -> None:
        super().__init__()
        self.regex = re.compile(r'event: ([a-z\-]+)\ndata: (.+)\n\n')
        self.connected = False

    @property
    def isConnected(self):
        return (self.connected)

    def on_mount(self) -> None:
        self.push_screen(LoginPage())

    @work
    async def SSE(self):
        if (not self.isConnected):
            self.connected = True
            # SSLContext = ssl.create_default_context()
            # SSLContext.load_verify_locations(Config.SSL.CRT)
            # SSLContext.check_hostname = False
            async with httpx.AsyncClient(verify=Config.SSL.CRT) as client:
                headers = {
                    'Content-Type': 'text/event-stream',
                    'Authorization': f'Bearer {User.accessToken}',
                }

                try:
                    async with client.stream('GET', f"{User.server}/sse/users/", headers=headers) as response:
                        if (response.status_code >= 400):
                            raise (Exception(f"({response.status_code}) SSE connection prout! {response.text}"))

                        async for line in response.aiter_text():
                            try:
                                events = self.regex.findall(line)
                                for event, data in events:
                                    dataJson = None
                                    # print(f"{event}")
                                    if (event == "game-start"):# game start
                                        dataJson = json.loads(data)
                                        # print(f"{event}: {dataJson}")
                                        if (dataJson["data"]["teams"]["a"]["players"][0]["id"] == User.id):
                                            User.team = "a"
                                            User.opponent = dataJson["data"]["teams"]["b"]["players"][0]["username"]
                                        else:
                                            User.team = "b"
                                            User.opponent = dataJson["data"]["teams"]["a"]["players"][0]["username"]
                                        # print(f"User opponent: {User.opponent}")
                                        await self.push_screen(GamePage())
                                    elif (event != "game-start" and event != "ping"):
                                    #   print(f"{event}: {data}")
                            except (IndexError, ValueError) as error:
                                continue
                finally:
                    self.connected = False

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        self.log(event)

