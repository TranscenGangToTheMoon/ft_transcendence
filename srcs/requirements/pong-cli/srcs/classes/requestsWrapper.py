import requests

class RequestsWrapper():
    def __init__(self, server: str | None = None):
        self.server: str | None = server
        self.SSLCertificate: str | None = None
        self.response: requests.Response | None = None
        self.headers = {"Content-Type": "application/json"}

    def get(self, path: str, data=None):
        if data is None:
            data = {}
        self.response = requests.get(url=f"{self.server}{path}", data=data, headers=self.headers, verify=self.SSLCertificate)

    def post(self, path: str, data=None):
        if data is None:
            data = {}
        self.response = requests.post(url=f"{self.server}{path}", data=data, headers=self.headers, verify=self.SSLCertificate)

    def put(self, path: str, data=None):
        if data is None:
            data = {}
        self.response = requests.put(url=f"{self.server}{path}", data=data, headers=self.headers, verify=self.SSLCertificate)
