# TODO Chat service

##

### 1) Socket

* Socket Created when the client start at least one conversation.

### 2) Selecting Menu

* Check and list the people he's able to chat with.
* When a person is selected, join the room with the chat id (if inexistent generate it).

### 3) SSE

* When the client is not in the room each message is received by sse event.
* The notifaction must contained the chat id.
* The client can join the room by clicking on the notification.

### 3) Join Discussion

* Need to check if he's allowed to join this conversation.
	1. if yes allow him in the room.
	2. if not block him.
* Display the chat page
* Load all the messages not readed + 5 and save the last message id.


### 3) Discussion process

* When the client send a message to the group save it in the db. (use api)
* If the client scroll back load the other message and update the last message id.
* Check regulary if the clients are connected.
	1. if not send side event for each message.
	2. if connected just send the message normaly.

### 4) Leave discussion

* Remove him from the group.
* Destroy the socket when all discussion leaved.


