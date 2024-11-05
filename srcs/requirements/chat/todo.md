# TODO Chat service

## process:

### 1) Chat menu opened

* Socket Created when the client start at least one conversation.
* While the socket is open, need to regulary check the connection (use ping/pong process).

### 2) Selecting the person to chat with

* Check people and list the ones he's able to chat with. (use api request)
* When a person is selected, create a groupe with the two client id.
* Save the group in the client.
* Create a box chat on the front page.
* Load the 5 last messages and save the last message id. 

### 3) Join Discussion

* When the client click on the notfication connect him if needed and add him to the group.
* Save the group in the client
* Create a box chat on the front page.
* Load all the messages not readed + 5 and save the last message id.


### 3) Discussion process

* When the client send a message to the group save it in the db. (use api)
* If the client scroll back load the other message and update the last message id.
* Check regulary if the clients are connected.
	1. if not send side event for each message.
	2. if connected just send the message normaly.
* If the connection is lost recreate the socket and re add the groups he was in.

### 4) Leave discussion

* Remove him from the group localy and on the server.
* Destroy the socket when all discussion leaved.


