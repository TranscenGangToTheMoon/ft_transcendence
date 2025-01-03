# Game Server Docs

# Game Server

## Basic working
The matchmaking service is always waiting for a new player, it handles a queue for each game modes and forms teams for each match it creates.

Once it has created a match it sends it to the game service that will create the instance of a match in it's own database and then send a request to the game server that is also a aiohttp/socketIO server.

The game server then creates it's own instance of a match in its cache and launches a dedicated thread to this match.
The thread can now wait for players for `GAME_PLAYER_CONNECT_TIMEOUT` seconds.

Once all players are connected it launches a countdown for 2 seconds and start the first point. Every point in the game will be the same operation as it.

And the game finshed, there is a winner! It's time to disconnect form the server. All clients will automatically be disconnected by the server and the match instance updated is saved in database, with funny informations such as 'against is own camp scores' or 'number of hits'

## connect via SocketIO

Once the game has been registered on the game server, the server-sent events service will inform all clients, they can connect to the socketIO server, it will automatically start the game once all players have join.

Here's a sample code to connect to the server:
```javascript
const host = window.location.origin;
let socket = io(host, {
    transports: ["websocket"],
    path: "/ws/game/",
    auth : {
        "id": userInformations.id,
        "token": '<token>',
        "match-code": '<match-code>', //only if you want to spectate
    },
});
//This comes from the javascript code included in the frontend
```

## authenticate as player
As you connect, you need to provide your aothentication token

If the id the client provided is registered as a player in a running game, it'll be accepted as a player and get player privileges

If the id the client provided is not registered as a player or there is no id field in auth, then the server will check for a match to spectate with the match code the client provided, if there is no match-code in the auth token, the connection will be refused.
You'll understand that everyone can spectate every online matches from the moment they have the valid match-code

## send input update
If the client is registered as a player, it'll have all players privileges from the server view. Meaning the client can send move_up, move_down, and stop_moving socketIO events and the server will listen for it

`move_up` : the client is moving up from now, it sends a `move_up` event that tells the server its racket is moving up.
```javascript
socket.emit('move_up');
```
`move_down` : the client is moving down from now, it sends a `move_down` event that tells the server its racket is moving down.
```javascript
socket.emit('move_down');
```
`stop_moving` : the client stopped moving, it sends a stop_moving event that tells the server it stopped moving and at what y coordinate the racket is.
```javascript
socket.emit('stop_moving', {'position': myRacket.y}
```

## receive game update
Once all players have connected to the game server, it will send the basic informations such as, what team you are (`'team_a'` or `'team_b'`) or the canvas size, needed by the client to match coordinates of the server or do approximations.

Here's how to handle it on JS:
```javascript
socket.on('team_id', event => {
	team = event.team;
})
socket.on('canvas', event => {
	canvas.height = event.canvas_height;
	canvas.width = event.canvas_width;
})
```

Every client successfully connected to the sockerIO game server will receive new events for the game they joined
The client needs to handle the same events it sends but in every events the server sends will be one more field designating the client that moved so it can retreive the right racket to update.

Here's a sample code form the JS web client we provide:
```javascript
socket.on('move_up', event => {
    console.log('move_up received');
    rackets[event.id].speed = -1;
})
socket.on('move_down', event => {
    console.log('move_down received');
    rackets[event.id].speed = 1;
})
socket.on('stop_moving', event => {
    console.log('received stop_moving')
    rackets[event.id].speed = 0;
    rackets[event.id].y = event.position;
})
```

The server will also send some game update every time the ball hits something, here is how to handle it in JS:
```javascript
socket.on('game_state', event => {
    ball.y = event.position_y;
    ball.x = event.position_x;
    ball.speedX = event.speed_x;
    ball.speedY = event.speed_y;
    ball.speed = event.speed;
})
```
