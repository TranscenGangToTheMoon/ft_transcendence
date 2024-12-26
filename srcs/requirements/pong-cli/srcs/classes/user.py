from .requestsWrapper import RequestsWrapper
import json

class User():
    def __init__(self, username: str | None = None, password: str | None = None):
        self.username: str | None = username
        self.password: str | None = password
        self.accessToken: str | None = None
        self.refreshToken: str | None = None

    def loginUser(self, r: RequestsWrapper):
        if (r.server is None):
            raise (Exception("Hostname not define"))

        data = json.dumps( {"username": self.username, "password": self.password})
        r.post("/api/auth/login/", data=data)
        print(r.response.json())
        if (r.response.status_code >= 300):
            if (r.response.json()["detail"] is not None):
                reason = r.response.json()["detail"]
            raise (Exception(f"({r.response.status_code}) Login failed: {reason}"))

        self.accessToken = r.response.json()["access"]
        self.refreshToken = r.response.json()["refresh"]
        r.headers["Authorization"] = "Bearer " + self.accessToken

    def guestUser(self, r: RequestsWrapper):
        if (r.server is None):
            raise (Exception("Hostname not define"))

        r.post("/api/auth/guest/")
        if (r.response.status_code >= 300):
            raise (Exception("Guest failed " + str(r.response.status_code)))

        self.accessToken = r.response.json()["access"]
        self.refreshToken = r.response.json()["refresh"]
        r.headers["Authorization"] = "Bearer " + self.accessToken

    def registerUser(self, r: RequestsWrapper):
        if (r.server is None):
            raise (Exception("Hostname not define"))

        data = json.dumps({"username": self.username, "password": self.password})
        r.post("/api/auth/register/", data=data)
        print(r.response.json())
        if (r.response.status_code >= 300):
            if (r.response.status_code == 401 and r.response.json()["code"] is not None):
                reason = r.response.json()["code"]
            else:
                reason = r.response.json()["username"]
            raise (Exception(f"({r.response.status_code}) Register failed: {reason}"))

        self.accessToken = r.response.json()["access"]
        self.refreshToken = r.response.json()["refresh"]
        r.headers["Authorization"] = "Bearer " + self.accessToken

    def registerGuestUser(self, r: RequestsWrapper):
        if (r.server is None):
            raise (Exception("Hostname not define"))
        if (self.accessToken is None or self.refreshToken is None):
            raise (Exception("Tokens not sets, please guest"))

        data = json.dumps({"username": self.username, "password": self.password})
        r.put("/api/auth/register/guest/", data=data)
        if (r.response.status_code >= 300):
            if (r.response.json()["username"] is not None):
                reason = r.response.json()["username"]
            raise (Exception(f"({r.response.status_code}) Register guest failed: {reason}"))

        self.accessToken = r.response.json()["access"]
        self.refreshToken = r.response.json()["refresh"]
        print(r.headers["Authorization"])
        r.headers["Authorization"] = "Bearer " + self.accessToken
        print(r.headers["Authorization"])

