# Python imports
import os
import argparse

# Local imports
from classes.PongCLIApp     import PongCLI
from classes.utils.config   import Config
from classes.utils.user     import User

def parser():
    parser = argparse.ArgumentParser(description='Pong game but in terminal')
    parser.add_argument(
        "-s", "--server",
        type=str,
        help="Server address",
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        help="Server port",
    )
    parser.add_argument(
        "-u", "--user",
        type=str,
        help="User name",
    )
    parser.add_argument(
        "-P", "--password",
        type=str,
        help="Password",
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        help="Configuration file",
        required=True
    )
    args = parser.parse_args()

    if (args.server is not None):
        User.server = args.server
    if (args.port is not None):
        User.port = args.port
    if (args.user is not None):
        User.username = args.user
    if (args.password is not None):
        User.password = args.password

    Config.load(args.config)

if __name__ == '__main__':
    parser()
    print(Config.__str__())

    Config.Console.width = 150
    Config.Console.height = 60
    os.system('clear')
    os.system(f'printf "\\e[8;{Config.Console.height};{Config.Console.width}t"')
    app = PongCLI()
    app.run()
