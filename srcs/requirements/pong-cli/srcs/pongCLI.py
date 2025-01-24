# Python imports
import argparse
import os
from urllib.parse import urlparse

# Local imports
from classes.PongCLIApp     import PongCLI
from classes.utils.config   import Config
from classes.utils.user     import User

def parser():
    parser = argparse.ArgumentParser(description='Pong game but in terminal')
    parser.add_argument(
        "-s", "--server",
        type=str,
        help="Server host (exemple: 127.0.0.1:4443)",
    )
    parser.add_argument(
        "-u", "--user",
        type=str,
        help="User name",
    )
    parser.add_argument(
        "-p", "--password",
        type=str,
        help="Password",
    )

    args = parser.parse_args()
    if (args.server is not None):
        User.server = args.server
    if (args.user is not None):
        User.username = args.user
    if (args.password is not None):
        User.password = args.password

    User.URI = f"https://{User.server}"
    User.host = urlparse(User.URI).hostname
    User.port = urlparse(User.URI).port

if __name__ == '__main__':
    parser()
    Config.Console.width = 160
    Config.Console.height = 60
    os.system('clear')
    os.system(f'printf "\\e[8;{Config.Console.height};{Config.Console.width}t"')
    app = PongCLI()
    app.run()
