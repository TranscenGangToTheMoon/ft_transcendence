import json
from operator import truediv

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Input, Static
from textual.containers import VerticalGroup, HorizontalGroup, Container, Horizontal, Vertical
from textual.worker import Worker, WorkerState
from textual import work
import requests
from classes.user import User
from enum import Enum


class Page(Enum):
    LoginPage = 1
    MainPage = 2
    GamePage = 3

class LoginPage(Screen):
    # def __init__(self):

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

    def compose(self) -> ComposeResult:
        yield Header()
        response = None
        try:
            response = requests.get(url=f"{User.server}/api/users/me/", data="", headers=User.headers, verify=User.SSLCertificate)
        except Exception as error:
            yield Static(f"({response.status_code}) /api/users/me/ Error: {error}")
        yield Static("Main page")
        yield Static(f"/api/users/me/ : {response.text}")
        yield Static("API users me results", id="status")
        yield Button("Dual", id="dualGame", variant="primary")
        yield Static("API play duel results", id="status2")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if (event.button.id == "dualGame"):
            self.dualGameAction()

    def dualGameAction(self):
        response = None
        try:
            response = requests.post(url=f"{User.server}/api/play/duel/", data="", headers=User.headers, verify=User.SSLCertificate)
        except Exception as error:
            self.query_one("#status2").update(f"({response.status_code}) Error: {error}")
        self.query_one("#status2").update(f"/api/play/duel/ : {response.text}")
        # while (gameWaitingForMe == false and notCancel)
            # spinner

class GamePage(Screen):

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Static("Game page")

import re
import json
import httpx

# diff on login and main page with Screen css ! Why ?
class PongCLI(App):
    CSS_PATH = [
        "../styles/LoginPage.tcss",
        "../styles/MainPage.tcss",
        "../styles/GamePage.tcss",
    ]
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
        self.push_screen(LoginPage())

    @work(exclusive=True)
    async def startSSE(self):
        if (not self.isConnected):
            # self.SSE = self.run_worker(SSEWorker)
            self.connected = True
            with httpx.AsyncClient(verify=User.SSLCertificate) as client:
                headers = {
                    'Content-Type': 'text/event-stream',
                    'Authorization': f'Bearer {User.accessToken}',
                }

                try:
                    async with client.stream('GET', f"{User.server}/sse/users/", headers=headers) as response:
                        if (response.status_code >= 400):
                            raise (Exception(f"({response.status_code}) SSE connection prout! {response.text}"))

                        # if (response.status_code == 200):
                        async for line in response.aiter_text():
                            if self.is_cancelled:
                                break

                            try:
                                events = self.regex.findall(line)
                                for event, data in events:
                                    if event == "game-start":# game start
                                        dataJson = json.loads(data)
                                        # await self.(self.GameStart(dataJson))
                                        self.log()
                                        # methode to send information to GameScreen / App

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
