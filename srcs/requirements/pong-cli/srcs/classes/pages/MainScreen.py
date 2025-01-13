# Python imports
import requests

# Textual imports
from textual.app        import ComposeResult
from textual.screen     import Screen
from textual.widgets    import Header, Footer, Rule, Button, Static

# Local imports
from classes.utils.user import User

from srcs.classes.utils.config import SSL_CRT


class MainPage(Screen):
    SUB_TITLE = "Main Page"
    CSS_PATH = "styles/MainPage.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        yield self.userMeStatic()
        yield Rule()
        yield Static("", id="duelResult")
        yield Button("Duel", id="duel", variant="primary")
        yield Rule()
        yield Static("", id="cancelDuelResult")
        yield Button("Cancel Duel", id="cancelDuelGame", variant="error", disabled=True)
        yield Rule()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if (event.button.id == "duel"):
            self.duelAction()
        elif (event.button.id == "cancelDuelGame"):
            self.cancelDuelAction()

    def duelAction(self):
        try:
            response = requests.post(url=f"{User.server}/api/play/duel/", data="", headers=User.headers, verify=SSL_CRT)
            if (response.status_code >= 400):
                raise (Exception(f"({response.status_code}) Error: {response.text}"))
            self.query_one("#duel").loading = True
            self.query_one("#duel").variant = "default"
            self.query_one("#cancelDuelGame").disabled = False
            self.query_one("#duelResult").update(f"({response.status_code}) Searching for an opponent")
        except Exception as error:
            self.query_one("#duelResult").update(f"POST /api/play/duel/ Error: {error}")

    def cancelDuelAction(self):
        try:
            response = requests.delete(url=f"{User.server}/api/play/duel/", data="", headers=User.headers, verify=SSL_CRT)
            if (response.status_code >= 400): #if 404 c'est que j'ai join le match maius oas recu le event SSE
                raise (Exception(f"({response.status_code}) Error: {response.text}"))
            elif (response.status_code == 204):
                self.query_one("#cancelDuelResult").update(f"({response.status_code}) DELETE /api/play/duel/ : Duel deleted")
                self.query_one("#duel").loading = False
                self.query_one("#duel").variant = "primary"
                self.query_one("#cancelDuelGame").disabled = True

        except Exception as error:
            self.query_one("#cancelDuelResult").update(f"DELETE /api/play/duel/ Error: {error}")

    def userMeStatic(self) -> Static:
        try:
            response = requests.get(url=f"{User.server}/api/users/me/", data={}, headers=User.headers, verify=SSL_CRT)
            User.id = response.json()["id"]
            return Static(f"({response.status_code}) GET /api/users/me/ : {response.text}")
        except Exception as error:
            return Static(f"GET /api/users/me/ Error: {error}")
