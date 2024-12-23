#!/bin/python3
import requests
from user import User
SSL_CRT = "/home/xcharra/Documents/42Projects/CommonCore/Rank6/ft_transcendence/secrets/ssl.crt"

def main():
    url = "https://localhost:4443/api/auth/guest/"
    headers = {
        "Content-Type": "application/json",
    }
    basil = User()
    basil.username = "basil"
    basil.password = "verysecurpass"

    basil.loginUser()

    response = requests.post(url, data='', verify=SSL_CRT, headers=headers)
    print(response.text)

if __name__ == '__main__':
    main()

