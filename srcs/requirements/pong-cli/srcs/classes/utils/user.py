# Python imports
import json
import requests

# Local imports
from classes.utils.config   import SSL_CRT


class User():
    accessToken: str | None = None
    headers = {"Content-Type": "application/json"}
    password: str | None = None
    refreshToken: str | None = None
    response: requests.Response | None = None
    server: str | None = None
    username: str | None = None
    id: int | None = None

    @staticmethod
    def loginUser():
        if (User.server is None):
            raise (Exception("Hostname not define"))

        data = json.dumps( {"username": User.username, "password": User.password})
        User.response = requests.post(url=f"{User.server}/api/auth/login/", data=data, headers=User.headers, verify=SSL_CRT)
        print(User.response.json())
        if (User.response.status_code >= 300):
            if (User.response.json()["detail"] is not None):
                reason = User.response.json()["detail"]
            raise (Exception(f"({User.response.status_code}) Login failed: {reason}"))

        User.accessToken = User.response.json()["access"]
        User.refreshToken = User.response.json()["refresh"]
        User.headers["Authorization"] = f"Bearer {User.accessToken}"

    @staticmethod
    def guestUser():
        if (User.server is None):
            raise (Exception("Hostname not define"))

        User.response = requests.post(url=f"{User.server}/api/auth/guest/", data={}, headers=User.headers, verify=SSL_CRT)
        if (User.response.status_code >= 300):
            raise (Exception("Guest failed " + str(User.response.status_code)))

        User.accessToken = User.response.json()["access"]
        User.refreshToken = User.response.json()["refresh"]
        User.headers["Authorization"] = f"Bearer {User.accessToken}"

    @staticmethod
    def registerUser():
        if (User.server is None):
            raise (Exception("Hostname not define"))

        data = json.dumps({"username": User.username, "password": User.password})
        User.response = requests.post(url=f"{User.server}/api/auth/register/", data=data, headers=User.headers, verify=SSL_CRT)
        print(User.response.json())
        if (User.response.status_code >= 300):
            if (User.response.status_code == 401 and User.response.json()["code"] is not None):
                reason = User.response.json()["code"]
            else:
                reason = User.response.json()["username"] #password too short issue
                # reason = User.response.json().get("username", "Unknown error")
            raise (Exception(f"({User.response.status_code}) Register failed: {reason}"))

        User.accessToken = User.response.json()["access"]
        User.refreshToken = User.response.json()["refresh"]
        User.headers["Authorization"] = f"Bearer {User.accessToken}"

    @staticmethod
    def registerGuestUser():
        if (User.server is None):
            raise (Exception("Hostname not define"))
        if (User.accessToken is None or User.refreshToken is None):
            raise (Exception("Tokens not sets, please guest"))

        data = json.dumps({"username": User.username, "password": User.password})
        User.response = requests.put(url=f"{User.server}/api/auth/register/guest/", data=data, headers=User.headers, verify=SSL_CRT)
        if (User.response.status_code >= 300):
            if (User.response.json()["username"] is not None):
                reason = User.response.json()["username"]
            raise (Exception(f"({User.response.status_code}) Register guest failed: {reason}"))

        User.accessToken = User.response.json()["access"]
        User.refreshToken = User.response.json()["refresh"]
        print(User.headers["Authorization"])
        User.headers["Authorization"] = f"Bearer {User.accessToken}"
        print(User.headers["Authorization"])

