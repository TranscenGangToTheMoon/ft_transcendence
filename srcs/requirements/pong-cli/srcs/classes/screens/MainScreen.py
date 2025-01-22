# Textual imports
from textual            import on
from textual.app        import ComposeResult
from textual.containers import Horizontal
from textual.screen     import Screen
from textual.widgets    import Button, Footer, Header, Label, Rule, Static

# Local imports
from classes.utils.user import User

class MainPage(Screen):
    SUB_TITLE = "Main Page"
    CSS_PATH = "styles/MainPage.tcss"
    BINDINGS = [("^q", "exit", "Exit"), ("ctrl+l", "logout", "Logout")]

    def __init__(self):
        super().__init__()
        self.searchDuel = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        yield Static("" , id="userMeStatic")
        yield Rule()
        with Horizontal(id="buttonBoxGame"):
            yield Button("Duel", id="duel", variant="primary")
            yield Button("Cancel Duel", id="cancelDuelGame", variant="error", disabled=True)
        yield Rule()
        yield Label("", id="statusGame")

    def on_mount(self):
        try:
            User.me()
            self.query_one("#userMeStatic").styles.color = "white"
            self.query_one("#userMeStatic").update(f"Welcome {User.username} (id: {User.id})")
        except Exception as error:
            self.query_one("#userMeStatic").styles.color = "red"
            if (User.response is not None and User.response.status_code == 401):
                code = User.response.json().get("code")
                if (code is not None and code == "token_not_valid"):
                    self.query_one("#userMeStatic").update("Tokens have expired please reconnect")
            else:
                self.query_one("#userMeStatic").update(f"{error}")

    def on_screen_resume(self) -> None:
        self.query_one("#duel").loading = False
        self.query_one("#duel").variant = "primary"
        self.query_one("#cancelDuelGame").disabled = True
        self.query_one("#statusGame").update("")

    def action_logout(self):
        if (self.searchDuel):
            self.cancelDuelAction()
        if (self.app.SSEConnected):
            self.app.stopSSE()
        User.logout()
        self.app.pop_screen()

    @on(Button.Pressed, "#duel")
    def duelAction(self):
        try:
            if (not self.app.SSEConnected):
                raise (Exception("SSE not connected ! Reconnect and try again."))
            User.duel()

            self.searchDuel = True
            self.query_one("#duel").loading = True
            self.query_one("#duel").variant = "default"
            self.query_one("#cancelDuelGame").disabled = False
            self.query_one("#statusGame").update(f"({User.response.status_code}) Searching for an opponent")

        except Exception as error:
            self.query_one("#statusGame").styles.color = "red"
            if (User.response is not None and User.response.status_code == 401):
                code = User.response.json().get("code")
                if (code is not None and code == "token_not_valid"):
                    self.query_one("#statusGame").update("Tokens have expired please reconnect")
            else:
                self.query_one("#statusGame").update(f"{error}")

    @on(Button.Pressed, "#cancelDuelGame")
    def cancelDuelAction(self):
        try:
            if (not self.app.SSEConnected):
                raise (Exception("SSE not connected ! Reconnect and try again."))
            User.cancelDuel()
            self.searchDuel = False
            self.query_one("#duel").loading = False
            self.query_one("#duel").variant = "primary"
            self.query_one("#statusGame").update("")
            self.query_one("#cancelDuelGame").disabled = True

        except Exception as error:
            self.query_one("#statusGame").styles.color = "red"
            if (User.response is not None and User.response.status_code == 401):
                code = User.response.json().get("code")
                if (code is not None and code == "token_not_valid"):
                    self.query_one("#statusGame").update("Tokens have expired please reconnect")
            else:
                self.query_one("#statusGame").update(f"{error}")
