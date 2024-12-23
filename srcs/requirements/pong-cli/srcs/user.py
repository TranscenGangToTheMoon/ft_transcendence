class User():
    def __init__(self, username: str | None = None, password: str | None = None):
        if (username is not None):
            self.username = username
        if (password is not None):
            self.password = password
        self.accessToken = None
        self.refreshToken = None

    def registerUser(self):
        pass

    def registerGuestUser(self):
        pass

    def loginUser(self):
        pass
