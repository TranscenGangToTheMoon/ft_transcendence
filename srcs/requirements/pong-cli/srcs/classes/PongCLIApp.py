# Python imports
import httpx
import json
import re

# Textual imports
from textual        import work
from textual.app    import App
from textual.worker import Worker, WorkerState

# Local imports
from classes.screens.GameScreen     import GamePage
from classes.screens.LoginScreen    import LoginPage
from classes.utils.config           import Config
from classes.utils.user             import User

class PongCLI(App):
    BINDINGS = [("^q", "exit", "Exit"), ]

    def __init__(self) -> None:
        super().__init__()
        self.regex = re.compile(r'event: ([a-z\-]+)\ndata: (.+)\n\n')
        self.SSEConnected = False

    def on_mount(self) -> None:
        self.push_screen(LoginPage())

    @work
    async def SSE(self):
        if (not self.SSEConnected):
            self.SSEConnected = True
            async with httpx.AsyncClient(verify=Config.SSL.CRT) as client:
                headers = {
                    'Content-Type': 'text/event-stream',
                    'Authorization': f'Bearer {User.accessToken}',
                }

                try:
                    async with client.stream('GET', f"https://{User.server}/sse/users/", headers=headers) as response:
                        if (response.status_code >= 400):
                            self.SSEConnected = False
                            raise (Exception(f"({response.status_code}) SSE stream failed {response.text}"))
                        try:
                            async for line in response.aiter_text():
                                try:
                                    events = self.regex.findall(line)
                                    for event, data in events:
                                        if (event == "game-start"):
                                            dataJson = json.loads(data)
                                            if (dataJson["data"]["teams"]["a"]["players"][0]["id"] == User.id):
                                                User.team = "a"
                                                User.opponent = dataJson["data"]["teams"]["b"]["players"][0]["username"]
                                            else:
                                                User.team = "b"
                                                User.opponent = dataJson["data"]["teams"]["a"]["players"][0]["username"]
                                            if (User.inAGame == False):
                                                await self.push_screen(GamePage())
                                        elif (event != "game-start" and event != "ping"):
                                            print(f"{event}: {data}")
                                except (IndexError, ValueError) as _:
                                    continue
                        except Exception as error:
                            self.SSEConnected = False
                            raise (Exception(f"Response aiter : {error}"))
                except Exception as _:
                    self.notify("SSE disconnected", severity="error", timeout=10)
                finally:
                    self.SSEConnected = False

    @work
    async def pushGamePage(self):
        await self.push_screen(GamePage())

    def stopSSE(self):
        if (self.SSEConnected == False):
            return
        for worker in self.workers:
            if (worker.name == "SSE"):
                self.SSEConnected = False
                worker.cancel()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if (event.worker.state == WorkerState.ERROR):
            print(f"Error from {event.worker.error}")
