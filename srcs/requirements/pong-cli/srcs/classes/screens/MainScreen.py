# Python imports
import requests

# Textual imports
from textual            import on
from textual.app        import ComposeResult
from textual.containers import Horizontal
from textual.screen     import Screen
from textual.widgets    import Button, Footer, Header, Label, Rule, Static

# Local imports
from classes.utils.config   import Config
from classes.utils.user     import User

class MainPage(Screen):
    SUB_TITLE = "Main Page"
    CSS_PATH = "styles/MainPage.tcss"

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
            response = requests.get(url=f"{User.server}/api/users/me/", data={}, headers=User.headers, verify=Config.SSL.CRT)
            User.id = response.json()["id"]
            self.query_one("#userMeStatic").update(f"Welcolme {response.json()['username']}\n(id: {User.id})")
        except Exception as error:
            self.query_one("#userMeStatic").update(f"GET /api/users/me/ Error: {error}")

    def on_screen_resume(self) -> None:
        self.query_one("#duel").loading = False
        self.query_one("#duel").variant = "primary"
        self.query_one("#cancelDuelGame").disabled = True
        self.query_one("#statusGame").update("")

    @on(Button.Pressed, "#duel")
    def duelAction(self):
        try:
            response = requests.post(url=f"{User.server}/api/play/duel/", data="", headers=User.headers, verify=Config.SSL.CRT)
            if (response.status_code >= 400):
                raise (Exception(f"({response.status_code}) Error: {response.text}"))
            self.query_one("#duel").loading = True
            self.query_one("#duel").variant = "default"
            self.query_one("#cancelDuelGame").disabled = False
            self.query_one("#statusGame").update(f"({response.status_code}) Searching for an opponent")
        except Exception as error:
            self.query_one("#statusGame").update(f"POST /api/play/duel/ Error: {error}")

    @on(Button.Pressed, "#cancelDuelGame")
    def cancelDuelAction(self):
        try:
            response = requests.delete(url=f"{User.server}/api/play/duel/", data="", headers=User.headers, verify=Config.SSL.CRT)
            if (response.status_code >= 400): #if 404 c'est que j'ai join le match maius oas recu le event SSE
                raise (Exception(f"({response.status_code}) Error: {response.text}"))
            elif (response.status_code == 204):
                self.query_one("#duel").loading = False
                self.query_one("#duel").variant = "primary"
                self.query_one("#cancelDuelGame").disabled = True

        except Exception as error:
            self.query_one("#cancelDuelResult").update(f"DELETE /api/play/duel/ Error: {error}")