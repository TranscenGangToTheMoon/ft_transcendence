# Python imports
import os
from urllib.parse import urlparse

# Textual imports
from textual import on, events
from textual.app        import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen     import Screen
from textual.widgets    import Button, Footer, Header, Input, Static

# Local imports
from classes.screens.MainScreen import MainPage
from classes.utils.config       import Config
from classes.utils.user         import User

class LoginPage(Screen):
    SUB_TITLE = "Login Page"
    CSS_PATH = "styles/LoginPage.tcss"

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

    def on_mount(self) -> None:
        self.query_one("#server").border_title = "Server"
        self.query_one("#server").styles.border_title_color = "white 50%"
        self.query_one("#server").styles.border_title_align = "right"
        self.query_one("#username").border_title = "Username"
        self.query_one("#username").styles.border_title_color = "white 50%"
        self.query_one("#username").styles.border_title_align = "right"
        self.query_one("#password").border_title = "Password"
        self.query_one("#password").styles.border_title_color = "white 50%"
        self.query_one("#password").styles.border_title_align = "right"
        self.query_one("#AuthenticationBox").border_title = "Authentication"

    def getSSLCertificate(self):
        User.host = urlparse(User.server).hostname
        User.port = urlparse(User.server).port
        if (User.host and User.port):
            os.system(f"openssl s_client -connect {User.host}:{User.port} -servername {User.host} </dev/null 2>/dev/null | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > {Config.SSL.CRT}")

    @on(Button.Pressed, "#loginButton")
    def loginAction(self):
        if (self.query_one("#server").value and self.query_one("#username").value and self.query_one("#password").value):
            User.server = self.query_one("#server").value
            User.username = self.query_one("#username").value
            User.password = self.query_one("#password").value
            try:
                self.getSSLCertificate()
                User.loginUser()
                self.query_one("#status").update(f"Status: login succeed!")
                self.app.startSSE()
                self.app.push_screen(MainPage())
            except Exception as error:
                if (User.response is not None):
                    self.query_one("#status").update(f"{error}")
                else:
                    self.query_one("#status").update(f"(666): {error}")
        else:
            self.query_one("#status").update(f"Empty fields")

    @on(Button.Pressed, "#registerButton")
    def registerAction(self):
        if (self.query_one("#server").value and self.query_one("#username").value and self.query_one("#password").value):
            User.server = self.query_one("#server").value
            User.username = self.query_one("#username").value
            User.password = self.query_one("#password").value
            try:
                self.getSSLCertificate()
                User.registerUser()
                self.query_one("#status").update(f"Status: register succeed!")
                self.app.startSSE()
                self.app.push_screen(MainPage())
            except Exception as error:
                if (User.response is not None):
                    self.query_one("#status").update(f"{error}")
                else:
                    self.query_one("#status").update(f"(666): {error}")
        else:
            self.query_one("#status").update(f"Empty fields")

    @on(Button.Pressed, "#guestUpButton")
    def guestUpAction(self):
        if (self.query_one("#server").value):
            User.server = self.query_one("#server").value
            try:
                self.getSSLCertificate()
                User.guestUser()
                self.app.startSSE()
                self.app.push_screen(MainPage())
            except Exception as error:
                if (User.response is not None):
                    self.query_one("#status").update(f"{error}")
                else:
                    self.query_one("#status").update(f"(666): {error}")
        else:
            self.query_one("#status").update(f"Empty fields")