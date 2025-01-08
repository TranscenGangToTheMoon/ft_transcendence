# Python imports
import requests

# Textual imports
from textual.app        import ComposeResult
from textual.screen     import Screen
from textual.widgets    import Header, Footer, Rule, Button, Static

# Local imports
from classes.utils.user import User


class MainPage(Screen):
    SUB_TITLE = "Main Page"
    CSS_PATH = "styles/MainPage.tcss"

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
            User.id = response.json()["id"]
            return Static(f"({response.status_code}) GET /api/users/me/ : {response.text}")
        except Exception as error:
            return Static(f"GET /api/users/me/ Error: {error}")
