import requests
import json

class RequestWrapper():
    def __init__(self, server: str | None = None):
        self.server: str | None = server
        self.SSLCertificate: str | None = None
        self.response: requests.Response | None = None
        # self.HTTPCode: int = 0
        self.headers = {"Content-Type": "application/json"}

    def get(self, path: str, data=None):
        if data is None:
            data = {}
        self.response = requests.get(url=self.server + path, data=data, headers=self.headers, verify=self.SSLCertificate)
        # self.HTTPCode = self.response.status_code

    def post(self, path: str, data=None):
        if data is None:
            data = {}
        self.response = requests.post(url=self.server + path, data=data, headers=self.headers, verify=self.SSLCertificate)
#         self.HTTPCode = self.response.status_code

    def put(self, path: str, data=None):
        if data is None:
            data = {}
        self.response = requests.put(url=self.server + path, data=data, headers=self.headers, verify=self.SSLCertificate)
#         self.HTTPCode = self.response.status_code

class User():
    def __init__(self, username: str | None = None, password: str | None = None):
        self.username: str | None = username
        self.password: str | None = password
        self.accessToken: str | None = None
        self.refreshToken: str | None = None

    def loginUser(self, r: RequestWrapper):
        if (r.server is None):
            raise (Exception("Hostname not define"))

        data = json.dumps( {"username": self.username, "password": self.password})
        r.post("/api/auth/login/", data=data)
        if (r.response.status_code >= 300):
            if (r.response.json()["detail"] is not None):
                reason = r.response.json()["detail"]
            raise (Exception(f"({r.response.status_code}) Register guest failed {reason}"))

        self.accessToken = r.response.json()["access"]
        self.refreshToken = r.response.json()["refresh"]
        r.headers["Authorization"] = "Bearer " + self.accessToken

    def guestUser(self, r: RequestWrapper):
        if (r.server is None):
            raise (Exception("Hostname not define"))

        r.post("/api/auth/guest/", )
        if (r.response.status_code >= 300):
            raise (Exception("Guest failed " + str(r.response.status_code)))

        self.accessToken = r.response.json()["access"]
        self.refreshToken = r.response.json()["refresh"]
        r.headers["Authorization"] = "Bearer " + self.accessToken

    def registerUser(self, r: RequestWrapper):
        if (r.server is None):
            raise (Exception("Hostname not define"))

        data = json.dumps( {"username": self.username, "password": self.password})
        r.post("/api/auth/register/", data=data)
        if (r.response.status_code >= 300):
            if (r.response.json()["username"] is not None):
                reason = r.response.json()["username"]
            raise (Exception(f"({r.response.status_code}) Register guest failed {reason}"))

        self.accessToken = r.response.json()["access"]
        self.refreshToken = r.response.json()["refresh"]
        r.headers["Authorization"] = "Bearer " + self.accessToken

    def registerGuestUser(self, r: RequestWrapper):
        if (r.server is None):
            raise (Exception("Hostname not define"))
        if (self.accessToken is None or self.refreshToken is None):
            raise (Exception("Tokens not sets, please guest"))

        data = json.dumps({"username": self.username, "password": self.password})
        r.put("/api/auth/register/guest/", data=data)
        if (r.response.status_code >= 300):
            if (r.response.json()["username"] is not None):
                reason = r.response.json()["username"]
            raise (Exception(f"({r.response.status_code}) Register guest failed {reason}"))

        self.accessToken = r.response.json()["access"]
        self.refreshToken = r.response.json()["refresh"]
        print(r.headers["Authorization"])
        r.headers["Authorization"] = "Bearer " + self.accessToken
        print(r.headers["Authorization"])

