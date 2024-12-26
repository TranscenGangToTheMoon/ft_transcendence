from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, Static
from textual.containers import VerticalGroup, HorizontalGroup, Container, Horizontal, Vertical

class AuthenticationPage(VerticalGroup):
    def compose(self) -> ComposeResult:
        with Vertical(id="AuthenticationBox"):
            yield Input(placeholder="Server", id="server")
            yield Input(placeholder="Username", id="username")
            yield Input(placeholder="Password", password=True, id="password")
            with Vertical(id="ButtonBox"):
                 with Horizontal():
                    yield Button("Login", variant="primary")
                    yield Button("Register", variant="primary")
                 yield Button("GuestUp", id="guest", variant="primary")
        yield Static("", id="status")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        server = self.query_one("#server").value
        username = self.query_one("#username").value
        password = self.query_one("#password").value
        self.query_one("#status").update(f"Status: {server} {username} {password}")
        if event.button.label == "Login":
            # Add login logic here
            pass
        elif event.button.label == "Register":
            # Add register logic here
            pass
        elif event.button.label == "GuestUp":
            # Add guest logic here
            pass

class PongCLI(App):
    CSS_PATH = "../styles/app.tcss"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield AuthenticationPage()
