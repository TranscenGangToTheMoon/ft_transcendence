# Python imports
import json
import requests

# Local imports
from classes.utils.config   import Config

class User():
    URI = None
    accessToken: str | None = None
    headers = {"Content-Type": "application/json"}
    host: str | None = None
    id: int | None = None
    inAGame: bool = False
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

        User.response = None
        data = json.dumps( {"username": User.username, "password": User.password})
        User.response = requests.post(
            url=f"https://{User.server}/api/auth/login/",
            data=data,
            headers=User.headers,
            verify=Config.SSL.verify,
            timeout=5
        )
        print(User.response)

        if (User.response.status_code == 200):
            User.accessToken = User.response.json()["access"]
            User.refreshToken = User.response.json()["refresh"]
            User.headers["Authorization"] = f"Bearer {User.accessToken}"
            return
        else:
            reason = "Unknown error"
            try:
                _ = User.response.json()
            except Exception as _:
                raise (Exception(f"({User.response.status_code})"))
            else:
                if (User.response.json().get("detail") is not None):
                    reason = f"{User.response.json()['detail']}"
                elif (User.response.json().get("username") is not None):
                    reason = f"{User.response.json()['username'][0]}"
                elif (User.response.json().get("password") is not None):
                    reason = f"{User.response.json()['password'][0]}"
            raise (Exception(f"({User.response.status_code}) {reason}"))

    @staticmethod
    def registerUser():
        if (User.server is None):
            raise (Exception("Hostname not define"))

        User.response = None
        data = json.dumps({"username": User.username, "password": User.password})
        User.response = requests.post(
            url=f"https://{User.server}/api/auth/register/",
            data=data,
            headers=User.headers,
            verify=Config.SSL.verify,
            timeout=5
        )
        print(User.response)

        if (User.response.status_code == 201):
            User.accessToken = User.response.json()["access"]
            User.refreshToken = User.response.json()["refresh"]
            User.headers["Authorization"] = f"Bearer {User.accessToken}"
            return
        else:
            reason = "Unknown error"
            try:
                _ = User.response.json()
            except Exception as _:
                raise (Exception(f"({User.response.status_code})"))
            else:
                if (User.response.json().get("detail") is not None):
                    reason = f"{User.response.json()['detail']}"
                elif (User.response.json().get("username") is not None):
                    reason = f"{User.response.json()['username'][0]}"
                elif (User.response.json().get("password") is not None):
                    reason = f"{User.response.json()['password'][0]}"
            raise (Exception(f"({User.response.status_code}) {reason}"))

    @staticmethod
    def guestUser():
        if (User.server is None):
            raise (Exception("Hostname not define"))

        User.response = None
        User.response = requests.post(
            url=f"https://{User.server}/api/auth/guest/",
            data={},
            headers=User.headers,
            verify=Config.SSL.verify,
            timeout=5
        )
        print(User.response)

        if (User.response.status_code == 201):
            User.accessToken = User.response.json()["access"]
            User.refreshToken = User.response.json()["refresh"]
            User.headers["Authorization"] = f"Bearer {User.accessToken}"
            return
        else:
            reason = "Unknown error"
            try:
                _ = User.response.json()
            except Exception as _:
                raise (Exception(f"({User.response.status_code})"))
            else:
                if (User.response.json().get("detail") is not None):
                    reason = f"{User.response.json()['detail']}"
                elif (User.response.json().get("username") is not None):
                    reason = f"{User.response.json()['username'][0]}"
                elif (User.response.json().get("password") is not None):
                    reason = f"{User.response.json()['password'][0]}"
            raise (Exception(f"({User.response.status_code}) {reason}"))

    @staticmethod
    def me():
        User.response = None
        User.response = requests.get(
            url=f"https://{User.server}/api/users/me/",
            data={},
            headers=User.headers,
            verify=Config.SSL.verify,
            timeout=5
        )
        print(User.response)

        if (User.response.status_code == 401):
            code = User.response.json().get("code")
            if (code is not None and code == "token_not_valid"):
                User.response = None
                User.refresh()
                User.response = requests.get(
                    url=f"https://{User.server}/api/users/me/",
                    data={},
                    headers=User.headers,
                    verify=Config.SSL.verify,
                    timeout=5
                )
                print(User.response)

        if (User.response.status_code == 401):
            code = User.response.json().get("code")
            raise (Exception(f"({User.response.status_code}) {Config.errorCodes[code]}"))
        elif (User.response.status_code != 200):
            try:
                _ = User.response.json()
            except Exception as _:
                raise (Exception(f"({User.response.status_code})"))
            else:
                detail = User.response.json().get("detail")
                raise (Exception(f"({User.response.status_code}) {detail}"))

        User.id = User.response.json()["id"]
        User.username = User.response.json()["username"]

    @staticmethod
    def duel():
        User.response = None
        User.response = requests.post(
            url=f"https://{User.server}/api/play/duel/",
            data="",
            headers=User.headers,
            verify=Config.SSL.verify,
            timeout=5
        )
        print(User.response)

        if (User.response.status_code == 401):
            code = User.response.json().get("code")
            if (code is not None and code == "token_not_valid"):
                User.response = None
                User.refresh()
                User.response = requests.post(
                    url=f"https://{User.server}/api/play/duel/",
                    data="",
                    headers=User.headers,
                    verify=Config.SSL.verify,
                    timeout=5
                )
                print(User.response)

        if (User.response.status_code == 401):
            code = User.response.json().get("code")
            raise (Exception(f"({User.response.status_code}) {Config.errorCodes[code]}"))
        elif (User.response.status_code != 201):
            try:
                _ = User.response.json()
            except Exception as _:
                raise (Exception(f"({User.response.status_code})"))
            else:
                detail = User.response.json().get("detail")
                raise (Exception(f"({User.response.status_code}) {detail}"))

    @staticmethod
    def cancelDuel():
        User.response = None
        User.response = requests.delete(
            url=f"https://{User.server}/api/play/duel/",
            data="",
            headers=User.headers,
            verify=Config.SSL.verify,
            timeout=5
        )
        print(User.response)

        if (User.response.status_code == 401):
            code = User.response.json().get("code")
            if (code is not None and code == "token_not_valid"):
                User.response = None
                User.refresh()
                User.response = requests.delete(
                    url=f"https://{User.server}/api/play/duel/",
                    data="",
                    headers=User.headers,
                    verify=Config.SSL.verify,
                    timeout=5
                )
                print(User.response)

        if (User.response.status_code == 401):
            code = User.response.json().get("code")
            raise (Exception(f"({User.response.status_code}) {Config.errorCodes[code]}"))
        elif (User.response.status_code != 204):
            try:
                _ = User.response.json()
            except Exception as _:
                raise (Exception(f"({User.response.status_code})"))
            else:
                detail = User.response.json().get("detail")
                raise (Exception(f"({User.response.status_code}) {detail}"))

    @staticmethod
    def refresh():
        User.response = None
        data = json.dumps({"refresh": User.refreshToken})
        User.response = requests.post(
            url=f"https://{User.server}/api/auth/refresh/",
            data=data,
            headers=User.headers,
            verify=Config.SSL.verify,
            timeout=5
        )
        print(User.response)

        if (User.response.status_code != 200):
            if (User.response.status_code == 401):
                try:
                    _ = User.response.json()
                except Exception as _:
                    raise (Exception(f"({User.response.status_code})"))
                else:
                    detail = User.response.json().get("detail")
                    raise (Exception(f"({User.response.status_code}) {detail}"))

        User.accessToken = User.response.json()["access"]
        User.headers["Authorization"] = f"Bearer {User.accessToken}"

    @staticmethod
    def logout():
        User.URI = None
        User.accessToken = None
        User.headers = {"Content-Type": "application/json"}
        User.host = None
        User.id = None
        User.inAGame = False
        User.opponent = None
        User.password = None
        User.port = None
        User.refreshToken = None
        User.response = None
        User.server = None
        User.team = None
        User.username = None
