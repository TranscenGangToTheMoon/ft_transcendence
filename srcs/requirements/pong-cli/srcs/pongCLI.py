# Python imports
import os

# Local imports
from classes.PongCLIApp     import PongCLI
from classes.utils.config   import Config

if __name__ == '__main__':
    Config.load("gameConfig.json")
    print(Config.__str__())

    width = 150
    height = 60
    os.system('clear')
    os.system(f'printf "\\e[8;{height};{width}t"')
    app = PongCLI()
    app.run()
