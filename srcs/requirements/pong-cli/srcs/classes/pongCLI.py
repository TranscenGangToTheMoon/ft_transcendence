from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, Static
from textual.containers import VerticalGroup, HorizontalGroup, Container, Horizontal, Vertical
from .user import User
from enum import Enum

class Page(Enum):
    LoginPage = 1
    MainPage = 2
    GamePage = 3

class AuthenticationPage(VerticalGroup):
    def __init__(self, user):
        super().__init__()
        self.user = user

    def compose(self) -> ComposeResult:
        with Vertical(id="AuthenticationBox"):
            yield Input(placeholder="Server", id="server", value="https://localhost:4443")
            yield Input(placeholder="Username", id="username", value="xcharra1234")
            yield Input(placeholder="Password", password=True, id="password", value="!@#$(90-9875trgfvcmntr")
            with Horizontal(id="ButtonBox"):
                yield Button("Login", id="loginButton", variant="primary")
                yield Button("Register", id="registerButton", variant="primary")
                yield Button("GuestUp", id="guestUpButton", variant="primary")
        yield Static("", id="status")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if (event.button.id == "loginButton"):
            self.loginAction()
        elif (event.button.id == "registerButton"):
            self.registerAction()
        elif (event.button.id == "guestUpButton"):
            self.guestUpAction()

    def loginAction(self):
        if (self.query_one("#server").value and self.query_one("#username").value and self.query_one("#password").value):
            self.user.server = self.query_one("#server").value
            self.user.username = self.query_one("#username").value
            self.user.password = self.query_one("#password").value
            try:
                self.user.loginUser()
                #change page
                self.query_one("#status").update(f"Status: login succeed!")
                #exit loop
            except Exception as error:
                if (self.user.response is not None):
                    self.query_one("#status").update(f"{error}")
                else:
                    self.query_one("#status").update(f"(666): {error}")
        else:
            self.query_one("#status").update(f"Empty fields")

    def registerAction(self):
        if (self.query_one("#server").value and self.query_one("#username").value and self.query_one("#password").value):
            self.user.server = self.query_one("#server").value
            self.user.username = self.query_one("#username").value
            self.user.password = self.query_one("#password").value
            try:
                self.user.registerUser()
                #change page
                self.query_one("#status").update(f"Status: register succeed!")
                #exit loop
            except Exception as error:
                if (self.user.response is not None):
                    self.query_one("#status").update(f"{error}")
                else:
                    self.query_one("#status").update(f"(666): {error}")
        else:
            self.query_one("#status").update(f"Empty fields")

    def guestUpAction(self):
        if (self.query_one("#server").value):
            self.user.server = self.query_one("#server").value
            try:
                self.user.guestUser()
                #change page
                self.query_one("#status").update(f"Status: GuestUp succeed!")
                #exit loop
            except Exception as error:
                if (self.user.response is not None):
                    self.query_one("#status").update(f"{error}")
                else:
                    self.query_one("#status").update(f"(666): {error}")
        else:
            self.query_one("#status").update(f"Empty fields")

class PongCLI(App):
    CSS_PATH = "../styles/AuthenticationPage.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self, user) -> None:
        super().__init__()
        self.user: User = user

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield AuthenticationPage(self.user)

    def changePage(self, page):
        match page:
            case Page.LoginPage:
                yield AuthenticationPage(self.user)
            case Page.MainPage:
                yield Static("MainPage")
            case Page.GamePage:
                yield Static("GamePage")
