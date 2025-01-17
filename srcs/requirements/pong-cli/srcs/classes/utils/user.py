# Python imports
import json
import requests

# Local imports
from classes.utils.config   import Config
from textual import log


class User():
    accessToken: str | None = None
    headers = {"Content-Type": "application/json"}
    id: int | None = None
    password: str | None = None
    refreshToken: str | None = None
    response: requests.Response | None = None
    server: str | None = None
    team: str | None = None
    username: str | None = None
    host: str | None = None
    port: int | None = None

    @staticmethod
    def loginUser():
        if (User.server is None):
            raise (Exception("Hostname not define"))

        data = json.dumps( {"username": User.username, "password": User.password})
        User.response = requests.post(url=f"{User.server}/api/auth/login/", data=data, headers=User.headers, verify=Config.SSL.CRT)
        # print(User.response.json())
        if (User.response.status_code != 200):
            reason = "Unknown error"
            if (User.response.json()["detail"] is not None):
                reason = f"Detail: {User.response.json()['detail']}"
            elif (User.response.json()["username"] is not None):
                reason = f"Username: {User.response.json()['username']}"
            elif (User.response.json()["password"] is not None):
                reason = f"Password: {User.response.json()['password']}"
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
            reason = "Unknown error"
            if (User.response.json()["detail"] is not None):
                reason = f"Detail: {User.response.json()['detail']}"
            elif (User.response.json()["username"] is not None):
                reason = f"Username: {User.response.json()['username']}"
            elif (User.response.json()["password"] is not None):
                reason = f"Password: {User.response.json()['password']}"
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
            reason = "Unknown error"
            if (User.response.status_code == 401):
                if (User.response.json()["detail"] is not None):
                    reason = f"Detail: {User.response.json()['detail']}"
                elif (User.response.json()["username"] is not None):
                    reason = f"Username: {User.response.json()['username']}"
                elif (User.response.json()["password"] is not None):
                    reason = f"Password: {User.response.json()['password']}"
            raise (Exception(f"({User.response.status_code}) {reason}"))

        User.accessToken = User.response.json()["access"]
        User.refreshToken = User.response.json()["refresh"]
        User.headers["Authorization"] = f"Bearer {User.accessToken}"
