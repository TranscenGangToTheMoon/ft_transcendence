# Python imports
import json
import requests

# Local imports
from classes.utils.config   import Config

class User():
    accessToken: str | None = None
    headers = {"Content-Type": "application/json"}
    host: str | None = None
    id: int | None = None
    opponent: str | None = None
    password: str | None = None
    port: int | None = None
    refreshToken: str | None = None
    response: requests.Response | None = None
    server: str | None = None
    team: str | None = None
    username: str | None = None

    @staticmethod
    def loginUser():
        if (User.server is None):
            raise (Exception("Hostname not define"))

        data = json.dumps( {"username": User.username, "password": User.password})
        User.response = requests.post(
            url=f"{User.server}/api/auth/login/",
            data=data,
            headers=User.headers,
            verify=Config.SSL.CRT
        )
        print(User.response.json())

        if (User.response.status_code != 200):
            reason = "Unknown error"
            if (User.response.json().get("detail") is not None):
                reason = f"{User.response.json()['detail']}"
            elif (User.response.json().get("username") is not None):
                reason = f"{User.response.json()['username'][0]}"
            elif (User.response.json().get("password") is not None):
                reason = f"{User.response.json()['password'][0]}"
            raise (Exception(f"({User.response.status_code}) {reason}"))

        User.accessToken = User.response.json()["access"]
        User.refreshToken = User.response.json()["refresh"]
        User.headers["Authorization"] = f"Bearer {User.accessToken}"

    @staticmethod
    def guestUser():
        if (User.server is None):
            raise (Exception("Hostname not define"))

        User.response = requests.post(
            url=f"{User.server}/api/auth/guest/",
            data={},
            headers=User.headers,
            verify=Config.SSL.CRT
        )
        print(User.response.json())

        if (User.response.status_code != 201):
            reason = "Unknown error"
            if (User.response.json().get("detail") is not None):
                reason = f"{User.response.json()['detail']}"
            elif (User.response.json().get("username") is not None):
                reason = f"{User.response.json()['username'][0]}"
            elif (User.response.json().get("password") is not None):
                reason = f"{User.response.json()['password'][0]}"
            raise (Exception(f"({User.response.status_code}) {reason}"))

        User.accessToken = User.response.json()["access"]
        User.refreshToken = User.response.json()["refresh"]
        User.headers["Authorization"] = f"Bearer {User.accessToken}"

    @staticmethod
    def registerUser():
        if (User.server is None):
            raise (Exception("Hostname not define"))

        data = json.dumps({"username": User.username, "password": User.password})
        User.response = requests.post(
            url=f"{User.server}/api/auth/register/",
            data=data,
            headers=User.headers,
            verify=Config.SSL.CRT
        )
        print(User.response.json())

        if (User.response.status_code != 201):
            reason = "Unknown error"
            if (User.response.json().get("detail") is not None):
                reason = f"{User.response.json()['detail']}"
            elif (User.response.json().get("username") is not None):
                reason = f"{User.response.json()['username'][0]}"
            elif (User.response.json().get("password") is not None):
                reason = f"{User.response.json()['password'][0]}"
            raise (Exception(f"({User.response.status_code}) {reason}"))

        User.accessToken = User.response.json()["access"]
        User.refreshToken = User.response.json()["refresh"]
        User.headers["Authorization"] = f"Bearer {User.accessToken}"

    @staticmethod
    def me():
        print("Me")
        User.response = requests.get(
            url=f"{User.server}/api/users/me/",
            data={},
            headers=User.headers,
            verify=Config.SSL.CRT
        )
        print(User.response)

        if (User.response.status_code != 200):
            if (User.response.status_code == 401):
                code = User.response.json().get("code")
                if (code is not None and code == "token_not_valid"):
                    User.refresh()
                    User.response = requests.get(
                        url=f"{User.server}/api/users/me/",
                        data={},
                        headers=User.headers,
                        verify=Config.SSL.CRT
                    )
                    print(User.response)

                if (User.response.status_code != 200):
                    raise (Exception(f"({User.response.status_code}) {User.response.json()}"))
            else:
                raise (Exception(f"({User.response.status_code}) {User.response.json()}"))

        User.id = User.response.json()["id"]
        User.username = User.response.json()["username"]

    @staticmethod
    def duel():
        print("Duel")
        User.response = requests.post(
            url=f"{User.server}/api/play/duel/",
            data="",
            headers=User.headers,
            verify=Config.SSL.CRT
        )
        print(User.response)

        if (User.response.status_code != 201):
            if (User.response.status_code == 401):
                User.refresh()
                User.response = requests.post(
                    url=f"{User.server}/api/play/duel/",
                    data="",
                    headers=User.headers,
                    verify=Config.SSL.CRT
                )
                print(User.response)

                if (User.response.status_code != 201):
                    raise (Exception(f"({User.response.status_code}) {User.response.json()}"))
            else:
                raise (Exception(f"({User.response.status_code}) {User.response.json()}"))

    @staticmethod
    def cancelDuel():
        print("Cancel duel")
        User.response = requests.delete(
            url=f"{User.server}/api/play/duel/",
            data="",
            headers=User.headers,
            verify=Config.SSL.CRT
        )

        if (User.response.status_code != 204):
            if (User.response.status_code == 401):
                User.refresh()
                User.response = requests.delete(
                    url=f"{User.server}/api/play/duel/",
                    data="",
                    headers=User.headers,
                    verify=Config.SSL.CRT
                )

                if (User.response.status_code != 204):
                    raise (Exception(f"({User.response.status_code}) {User.response.json()}"))
            else:
                raise (Exception(f"({User.response.status_code}) {User.response.json()}"))

    @staticmethod
    def refresh():
        print("Refresh token")
        data = json.dumps({"refresh": User.refreshToken})
        User.response = requests.post(
            url=f"{User.server}/api/auth/refresh/",
            data=data,
            headers=User.headers,
            verify=Config.SSL.CRT
        )
        print(User.response)

        if (User.response.status_code != 200):
            if (User.response.status_code == 401):
                raise (Exception(f"({User.response.status_code}) {User.response.json()}"))

        User.accessToken = User.response.json()["access"]
        User.headers["Authorization"] = f"Bearer {User.accessToken}"

    @staticmethod
    def logout():
        User.accessToken = None
        User.headers = {"Content-Type": "application/json"}
        User.host = None
        User.id = None
        User.opponent = None
        User.password = None
        User.port = None
        User.refreshToken = None
        User.response = None
        User.server = None
        User.team = None
        User.username = None
