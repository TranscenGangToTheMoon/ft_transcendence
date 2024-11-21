# Game Server

## the server launcher

### Server launcher must be able to:
-   create a new server

## the server

### Server must be able to:
-   bind an available port (is there are available ports)
-   send an error message to a service if it can't bind a port
-   retreive a the match informations from django ORM with the match code
-   retreive a racket from a Socket ID (sid)
-   update a view of the game
-   broadcast elments of the view to all clients
