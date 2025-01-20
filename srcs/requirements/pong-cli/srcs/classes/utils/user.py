# Python imports
import json
import requests

# Local imports
from classes.utils.config   import Config
from textual import log


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
        User.response = requests.post(url=f"{User.server}/api/auth/login/", data=data, headers=User.headers, verify=Config.SSL.CRT)
        if (User.response.status_code != 200):
            log(User.response.json())
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

        User.response = requests.post(url=f"{User.server}/api/auth/guest/", data={}, headers=User.headers, verify=Config.SSL.CRT)
        if (User.response.status_code != 201):
            log(User.response.json())
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
        User.response = requests.post(url=f"{User.server}/api/auth/register/", data=data, headers=User.headers, verify=Config.SSL.CRT)
        print(User.response.json())

        if (User.response.status_code != 201):
            log(User.response.json())
            reason = "Unknown error"
            # if (User.response.status_code == 401):
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
    def reset():
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
