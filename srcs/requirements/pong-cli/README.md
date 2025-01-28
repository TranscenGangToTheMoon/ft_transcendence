# pongCLI
pongCLI is a command-line-based implementation of the classic game Pong.
This project brings the nostalgic gameplay of Pong into your terminal,
allowing players to play directly from the CLI against players using the web version of the game.
It's lightweight, easy to use, and perfect for retro gaming enthusiasts.

## Features
- Duel game
- Lightweight and efficient terminal-based gameplay
- Keyboard controls for responsive gameplay (Arrow-Up Arrow-Down)

## Getting Started
Follow the instructions below to set up and play pongCLI on your local machine.

### Prerequisites
Ensure that a virtual environment is created and activated before running the CLI. This helps in managing dependencies
efficiently.

Create a virtual environment (if not already present):
```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
```
Or use Makefile command:
```bash
    make
```

### Usage
Make sure the pong server is up.

Run the following command to start the game:
```bash
   python srcs/pongCLI.py
```
Or use Makefile command:
```bash
   make run
```

You can add flags to facilitate authentication:
```bash
   pongCLI.py [-h] [-s SERVER] [-u USER] [-p PASSWORD]
```
Options:
- `-h`, `--help` : show this help message and exit
- `-s <SERVER>`, `--server <SERVER>` : Server host (exemple: 127.0.0.1:4443)
- `-u <USER>`, `--user <USER>` : Username (exemple xcharra)
- `-p <PASSWORD>`, `--password <PASSWORD>` : (exemple Azerty42)

You can use the following command
```bash
    python srcs/pongCLI.py -s 10.13.5.2:4443 -u xcharra -p Azerty42
```
Or use Makefile command:
```bash
    make run CLI_FLAGS="-s 10.13.5.2:4443 -u xcharra -p Azerty42"
```

Controls:
- Press `Arrow-Up` to move the paddle up.
- Press `Arrow-Down` to move the paddle down.
- Press `^Q` to exit the CLI.
- Press `^L` to logout of the CLI.
- Press `f` to quit the current game.

## Acknowledgments
- Inspired by the original Pong game.
- Thanks to the open-source community for supporting projects like this.

---
Enjoy playing pongCLI! 🎮
