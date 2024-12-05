# Game Server and Game Server Launcher Docs

## Game Server Launcher

The Game Server Launcher is an automated program ran from a django view matching a PUT request on /api/match
This means a PUT request on .../api/match with the corresponding API informations provided will make the code run

When the view is requested, the Django server will create a subprocess and run a Game Server with forwarded stdout, it will then read stdout from this subprocess until it gets an output matching the regex ```r'^Port:\s(\d+)\n?'```\
Getting the right output makes the django server stopping listening to the subprocess meaning that the server is started and doesn't need being monitored anymore, it'll make its life by itself
Once the django server got the port (on success of the subprocess to bind a port), it can push it to another service that remains always connected with the client to give it the information that a port has been binded for that specific game and it can now begin a direct socketIO connection to the all-new Game Server.

## Game Server

### Basic working

The Game Server starts automatically after a match has been processed by django, it will bind an available port on the server between ```GAME_SERVER_MIN_PORT``` and ```GAME_SERVER_MAX_PORT```.\
Once the port is bind, the server will wait for player connecting and start a game once every player is connected.\
To connect, a player needs to have a valid authentication token that lets it play the game (he must be part of the match) if he's not authenticated as a player in that game, the server will only send him informations about the game and consider he's just spectating.\
The server will not listen any information coming from a viewer.\
If the user is authenticated as a player for this match then the server will listen to every input from that client and update the game in subconsequently

The Game Server will send every client via SocketIO all informations and update on the running game but only listen for inputs from authenticated players for this game

As the server is on the same container as the django server and written in the same language (python), it can use the Django ORM to communicate with the DataBase, really easing the communication between those independant servers.

### connect via SocketIO

### authenticate as player

### send input update

### receive game update
