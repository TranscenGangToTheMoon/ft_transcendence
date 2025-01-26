# Python imports
import os
import requests
from urllib.parse import urlparse

# Textual imports
from textual            import on
from textual.app        import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen     import Screen
from textual.widgets    import Button, Footer, Header, Input, Label

# Local imports
from classes.screens.MainScreen import MainPage
from classes.utils.config       import Config
from classes.utils.user         import User

class LoginPage(Screen):
    SUB_TITLE = "Login Page"
    CSS_PATH = "styles/LoginPage.tcss"
    BINDINGS = [("^q", "exit", "Exit"), ]
    def __init__(self):
        super().__init__()

        self.server = f"https://{User.server}" if (User.server is not None) else ""
        self.username = User.username if (User.username is not None) else ""
        self.password = User.password if (User.password is not None) else ""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="authenticationBox"):
            yield Input(placeholder="Server", id="server", value=f"{self.server}")
            yield Input(placeholder="Username", id="username", value=f"{self.username}")
            yield Input(placeholder="Password", password=True, id="password", value=f"{self.password}")
            with Horizontal(id="buttonBox"):
                yield Button("Login", id="loginButton", variant="primary")
                yield Button("Register", id="registerButton", variant="primary")
                yield Button("GuestUp", id="guestUpButton", variant="primary")
        yield Label("", id="status")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#server").border_title = "Server"
        self.query_one("#username").border_title = "Username"
        self.query_one("#password").border_title = "Password"
        self.query_one("#authenticationBox").border_title = "Authentication"

    def on_screen_resume(self) -> None:
        self.query_one("#status").styles.color = "white"
        self.query_one("#status").update("")

    def getSSLAndJSON(self):
        User.host = urlparse(User.URI).hostname
        User.port = urlparse(User.URI).port
        User.server = f"{User.host}:{User.port}"
        if (User.host and User.port):
            os.system(f"echo | openssl s_client -connect {User.host}:{User.port} -servername {User.host} 2>/dev/null | sed -ne '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/p' > {Config.SSL.CRT}")

            result = os.system(f"openssl x509 -in {Config.SSL.CRT} -noout 2>/dev/null")
            if (result != 0):
                raise (Exception(f"Certificate retrieval failed"))
        jsonData = {}

        response = requests.get(
            url=f"https://{User.server}/gameConfig.json",
            verify=Config.SSL.CRT
        )
        if (
            response is not None
            and response.status_code == 200
            and response.headers["Content-Type"] == "application/json"
        ):
            jsonData = response.json()
        Config.load(jsonData)

    @on(Button.Pressed, "#loginButton")
    def loginAction(self):
        if (
            self.query_one("#server").value
            and self.query_one("#username").value
            and self.query_one("#password").value
        ):
            User.URI = self.query_one("#server").value
            User.username = self.query_one("#username").value
            User.password = self.query_one("#password").value
            try:
                self.getSSLAndJSON()
                User.loginUser()
                self.app.SSE()
                self.app.push_screen(MainPage())
            except Exception as error:
                if (User.response is not None):
                    self.query_one("#status").update(f"{error}")
                    self.query_one("#status").styles.color = "red"
                else:
                    self.query_one("#status").update(f"(666): {error}")
        else:
            self.query_one("#status").update(f"Empty fields")

    @on(Button.Pressed, "#registerButton")
    def registerAction(self):
        if (
            self.query_one("#server").value
            and self.query_one("#username").value
            and self.query_one("#password").value
        ):
            User.URI = self.query_one("#server").value
            User.username = self.query_one("#username").value
            User.password = self.query_one("#password").value
            try:
                self.getSSLAndJSON()
                User.registerUser()
                self.app.SSE()
                self.app.push_screen(MainPage())
            except Exception as error:
                if (User.response is not None):
                    self.query_one("#status").update(f"{error}")
                    self.query_one("#status").styles.color = "red"
                else:
                    self.query_one("#status").update(f"(666): {error}")
        else:
            self.query_one("#status").update(f"Empty fields")

    @on(Button.Pressed, "#guestUpButton")
    def guestUpAction(self):
        if (self.query_one("#server").value):
            User.URI = self.query_one("#server").value
            try:
                self.getSSLAndJSON()
                User.guestUser()
                self.app.SSE()
                self.app.push_screen(MainPage())
            except Exception as error:
                if (User.response is not None):
                    self.query_one("#status").update(f"{error}")
                    self.query_one("#status").styles.color = "red"
                else:
                    self.query_one("#status").update(f"(666): {error}")
        else:
            self.query_one("#status").update(f"Empty fields")
