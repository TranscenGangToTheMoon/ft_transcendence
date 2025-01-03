from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Input, Static, Rule, LoadingIndicator
from textual.containers import VerticalGroup, HorizontalGroup, Container, Horizontal, Vertical
from textual.worker import Worker, WorkerState
from textual.geometry import Region, Offset
from textual import work, events
from textual import log
import requests
from classes.user import User

class LoginPage(Screen):
    SUB_TITLE = "Login Page"
    CSS_PATH = "../styles/LoginPage.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="AuthenticationBox"):
            yield Input(placeholder="Server", id="server", value="https://localhost:4443")
            yield Input(placeholder="Username", id="username", value="xcharra1234")
            yield Input(placeholder="Password", password=True, id="password", value="!@#$(90-9875trgfvcmntr")
            with Horizontal(id="ButtonBox"):
                yield Button("Login", id="loginButton", variant="primary")
                yield Button("Register", id="registerButton", variant="primary")
                yield Button("GuestUp", id="guestUpButton", variant="primary")
        yield Static("", id="status")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if (event.button.id == "loginButton"):
            self.loginAction()
        elif (event.button.id == "registerButton"):
            self.registerAction()
        elif (event.button.id == "guestUpButton"):
            self.guestUpAction()

    def loginAction(self):
        if (self.query_one("#server").value and self.query_one("#username").value and self.query_one("#password").value):
            User.server = self.query_one("#server").value
            User.username = self.query_one("#username").value
            User.password = self.query_one("#password").value
            try:
                User.loginUser()
                # User
                self.query_one("#status").update(f"Status: login succeed!")
                self.app.startSSE() #maybe is okay bc I add this method to my App
                self.app.push_screen(MainPage())
                #exit loop
            except Exception as error:
                if (User.response is not None):
                    self.query_one("#status").update(f"{error}")
                else:
                    self.query_one("#status").update(f"(666): {error}")
        else:
            self.query_one("#status").update(f"Empty fields")

    def registerAction(self):
        if (self.query_one("#server").value and self.query_one("#username").value and self.query_one("#password").value):
            User.server = self.query_one("#server").value
            User.username = self.query_one("#username").value
            User.password = self.query_one("#password").value
            try:
                User.registerUser()
                self.query_one("#status").update(f"Status: register succeed!")
                self.app.startSSE() #maybe is okay bc I add this method to my App
                self.app.push_screen(MainPage())
                #exit loop
            except Exception as error:
                if (User.response is not None):
                    self.query_one("#status").update(f"{error}")
                else:
                    self.query_one("#status").update(f"(666): {error}")
        else:
            self.query_one("#status").update(f"Empty fields")

    def guestUpAction(self):
        if (self.query_one("#server").value):
            User.server = self.query_one("#server").value
            try:
                User.guestUser()
                # self.query_one("#status").update(f"Status: GuestUp succeed!")
                self.app.push_screen(MainPage())
                #exit loop
            except Exception as error:
                if (User.response is not None):
                    self.query_one("#status").update(f"{error}")
                else:
                    self.query_one("#status").update(f"(666): {error}")
        else:
            self.query_one("#status").update(f"Empty fields")

class MainPage(Screen):
    SUB_TITLE = "Main Page"
    CSS_PATH = "../styles/MainPage.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        yield self.userMeStatic()
        yield Rule()
        yield Button("Duel", id="duel", variant="primary")
        # change this button Widget.loading to true to transform it into loading bar when it pressed and requete made
        yield Static("POST /api/play/duel/", id="duelResult")
        yield Rule()
        yield Button("Cancel Duel", id="cancelDuelGame", variant="error")
        yield Static("DELETE /api/play/duel/", id="cancelDuelResult")
        yield Rule()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if (event.button.id == "duel"):
            self.duelAction()
        elif (event.button.id == "cancelDuelGame"):
            self.cancelDuelAction()

    def duelAction(self):
        try:
            response = requests.post(url=f"{User.server}/api/play/duel/", data="", headers=User.headers, verify=User.SSLCertificate)
            if (response.status_code >= 400):
                raise (Exception(f"({response.status_code}) Error: {response.text}"))
            self.query_one("#duelResult").update(f"({response.status_code}) POST /api/play/duel/ : {response.text}")
        except Exception as error:
            self.query_one("#duelResult").update(f"POST /api/play/duel/ Error: {error}")

    def cancelDuelAction(self):
        try:
            response = requests.delete(url=f"{User.server}/api/play/duel/", data="", headers=User.headers, verify=User.SSLCertificate)
            if (response.status_code >= 400): #if 404 c'est que j'ai join le match maius oas recu le event SSE
                raise (Exception(f"({response.status_code}) Error: {response.text}"))
            elif (response.status_code == 204):
                self.query_one("#cancelDuelResult").update(f"({response.status_code}) DELETE /api/play/duel/ : Duel deleted")
        except Exception as error:
            self.query_one("#cancelDuelResult").update(f"DELETE /api/play/duel/ Error: {error}")

    def userMeStatic(self) -> Static:
        try:
            response = requests.get(url=f"{User.server}/api/users/me/", data={}, headers=User.headers, verify=User.SSLCertificate)
            return Static(f"({response.status_code}) GET /api/users/me/ : {response.text}")
        except Exception as error:
            return Static(f"GET /api/users/me/ Error: {error}")

from textual.widget import Widget
from rich.console import Console

class Playground(Widget):
    def __init__(self):
        super().__init__()
        self.styles.width = 115
        self.styles.height = 40
        log("Playground:")
        log(self.offset)
        log(self.region)

    def render(self):
        return "                                                      █\n" * self.region.width

    def on_mount(self):
        console = Console()
        screen_width = console.width
        screen_height = console.height

        log("=======")
        log(self.region.width)
        log(self.region.height)
        log(self.styles.width)
        log(self.styles.height)
        log("=======")
        x_offset = (screen_width - int(self.styles.width.value)) // 2
        y_offset = (screen_height - int(self.styles.height.value)) // 2
        # x_offset = (screen_width - self.region.width) // 2
        # y_offset = (screen_height - self.region.height) // 2

        log(x_offset)
        log(y_offset)
        self.styles.offset = Offset(x_offset, y_offset)
        self.styles.background = "blue"
        # self.styles.border = ("solid", "white")

    # def on_resize(self, event: events.Resize):
    #     pass

class PaddleLeft(Widget):
    def __init__(self):
        super().__init__()

        self.offset = Offset(14, 0)
        # self.region = Region(0, 0, 4, 13)
        self.terrain_width = 4
        self.terrain_height = 13
        # log("Paddle Left:")
        # log(self.offset)
        # log(self.region)

    def render(self):
        return "█" * self.terrain_height * self.terrain_width

    def on_mount(self):
        self.styles.width = str(self.terrain_width)
        self.styles.height = str(self.terrain_height)

        # self.styles.offset = Offset(14, 0)
        self.styles.background = "white"

class GamePage(Screen):
    SUB_TITLE = "Game Page"
    CSS_PATH = "../styles/GamePage.tcss"


    def compose(self) -> ComposeResult:
        yield Header()
        with Playground():
            yield PaddleLeft()
        yield Button("Exit Button", id="exitAction")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if (event.button.id == "exitAction"):
            self.dismiss()

import re
import json
import httpx

# diff on login and main page with Screen css ! Why ?
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
