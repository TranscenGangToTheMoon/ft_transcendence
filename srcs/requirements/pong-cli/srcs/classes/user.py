import json
import requests
from requests import Response


class User():
    def __init__(self, username: str | None = None, password: str | None = None):
        self.SSLCertificate: str | None = None
        self.accessToken: str | None = None
        self.headers = {"Content-Type": "application/json"}
        self.password: str | None = None
        self.refreshToken: str | None = None
        self.response: Response | None = None
        self.server: str | None = None
        self.username: str | None = None

    def loginUser(self):
        if (self.server is None):
            raise (Exception("Hostname not define"))

        data = json.dumps( {"username": self.username, "password": self.password})
        self.response = requests.post(url=f"{self.server}/api/auth/login/", data=data, headers=self.headers, verify=self.SSLCertificate)
        print(self.response.json())
        if (self.response.status_code >= 300):
            if (self.response.json()["detail"] is not None):
                reason = self.response.json()["detail"]
            raise (Exception(f"({self.response.status_code}) Login failed: {reason}"))

        self.accessToken = self.response.json()["access"]
        self.refreshToken = self.response.json()["refresh"]
        self.headers["Authorization"] = f"Bearer {self.accessToken}"

    def guestUser(self):
        if (self.server is None):
            raise (Exception("Hostname not define"))

        self.response = requests.post(url=f"{self.server}/api/auth/guest/", data={}, headers=self.headers, verify=self.SSLCertificate)
        if (self.response.status_code >= 300):
            raise (Exception("Guest failed " + str(self.response.status_code)))

        self.accessToken = self.response.json()["access"]
        self.refreshToken = self.response.json()["refresh"]
        self.headers["Authorization"] = f"Bearer {self.accessToken}"

    def registerUser(self):
        if (self.server is None):
            raise (Exception("Hostname not define"))

        data = json.dumps({"username": self.username, "password": self.password})
        self.response = requests.post(url=f"{self.server}/api/auth/register/", data=data, headers=self.headers, verify=self.SSLCertificate)
        print(self.response.json())
        if (self.response.status_code >= 300):
            if (self.response.status_code == 401 and self.response.json()["code"] is not None):
                reason = self.response.json()["code"]
            else:
                reason = self.response.json()["username"]
            raise (Exception(f"({self.response.status_code}) Register failed: {reason}"))

        self.accessToken = self.response.json()["access"]
        self.refreshToken = self.response.json()["refresh"]
        self.headers["Authorization"] = f"Bearer {self.accessToken}"

    def registerGuestUser(self):
        if (self.server is None):
            raise (Exception("Hostname not define"))
        if (self.accessToken is None or self.refreshToken is None):
            raise (Exception("Tokens not sets, please guest"))

        data = json.dumps({"username": self.username, "password": self.password})
        self.response = requests.put(url=f"{self.server}/api/auth/register/guest/", data=data, headers=self.headers, verify=self.SSLCertificate)
        if (self.response.status_code >= 300):
            if (self.response.json()["username"] is not None):
                reason = self.response.json()["username"]
            raise (Exception(f"({self.response.status_code}) Register guest failed: {reason}"))

        self.accessToken = self.response.json()["access"]
        self.refreshToken = self.response.json()["refresh"]
        print(self.headers["Authorization"])
        self.headers["Authorization"] = f"Bearer {self.accessToken}"
        print(self.headers["Authorization"])

