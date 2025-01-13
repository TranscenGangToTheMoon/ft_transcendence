# Python imports
import os

# Local imports
from classes.PongCLIApp import PongCLI

if __name__ == '__main__':
    os.system('clear')
    os.system('printf "\\e[8;60;150t"')
    app = PongCLI()
    app.run()
