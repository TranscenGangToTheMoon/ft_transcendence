# API Documentation


### URL base
```
https://localhost:4443/api/
```


## Authentication
The API uses an authentication system based on **JSON Web Tokens (JWT)**.

### Obtaining a token
```
POST /auth/login/
```
- **Body (JSON)** :
  ```json
  {
    "*username": "str",
    "*password": "str"
  }
  ```
- **Response (success)** :
  ```json
  {
    "access": "str",
    "refresh": "str"
  }
  ```

### Access Token
Pour accéder aux endpoints protégés, ajoutez le token dans l'en-tête `Authorization` :
```
Authorization: Bearer <access_token>
```

### Endpoints with authentication
All endpoints marked with 🔒 require authentication. These endpoints correspond to requests that communicate with the front end (this is the public API).

### Response codes
- `200 OK` : Query successful.
- `201 Created`: Resource created.
- `204 No Content` : Successful request without body return (often used when deleting an instance).
- `400 Bad Request` : Validation error.
- `401 Unauthorized` : Authentication required.
- `403 Permission Denied`: The client does not have access rights to the content (unlike 401, the client's identity is known to the server).
- `404 Not Found` : Resource not found.
- `405 Method Not Allowed` : Request method not authorized.
- `409 Conflict` : Conflict during request (often when the client tries to create a resource that already exists).
- `415 Unsupported Media Type` : The requested *content-type* format is not supported by the server.
- `429 Throttled`: All **POST**, **PUT** and **PATCH** requests may return this error. This happens when many requests are sent at exactly the same time. The error details are always the same: *"Request was throttled. ”*.
- `500 Internal Server Error`: Server-side error.
- `502 Bad Gateway`: This error response means that the server has received an invalid response.
- `503 Service Unavailable`: The server is not ready to process the request (in our case, because a micro-service other than the requesting one is no longer working).

## Pagination
The API uses a pagination system based on the **`limit`** and **`offset`** parameters to efficiently manage large numbers of responses.

- **`limit`**: Defines the maximum number of elements to be returned in a response.
  - Default: `20` (if not specified).
  - Example: `?limit=50` will return a maximum of 50 elements.

- **`offset`**: Defines the starting point for elements to be included in the response.
  - Default: `0` (if not specified).
  - Example: `?offset=40` will start returning elements from 41ᵉ.

### Example
If the API contains 100 elements:
- A query with `?limit=10&offset=20` returns elements from index 21 to 30.

### Response with pagination
```json
{
  "count": "int",
  "next": "https://localhost:4443/api/resource/?limit=10&offset=30",
  "previous": "https://localhost:4443/api/resource/?limit=10&offset=10",
  "results": []
}
```
- ***count***: Total number of elements
- ***next***: URL of next page
- ***previous***: URL of previous page
- ***results*** : List of paginated elements

The **`next`** and **`previous`** fields can be set to `null` if there is no link to a previous or next page.

### Body
All fields preceded by `*` are required.
Field types correspond to the type used in _python_.
When a field can be filled in a `GET` request, it must be filled in the request URL in the form: `url/?field_name=field_value`.


# Auth

### Base URL
```
https://localhost:4443/api/auth/
```
## Connection

```
POST https://localhost:4443/api/auth/login/
```
- **Description** : Allows users to log in by providing their login details.
- **Body (JSON)** :
  ```json
  {
    "*username": "str",
    "*password": "str"
  }
  ```
- **Response (success)** :
  ```json
  {
    "access": "str",
    "refresh": "str"
  }
  ```
- **Response codes** :
    - `200 OK`
    - `401 Unauthorized`

## Guest
```
POST https://localhost:4443/api/auth/guest/
```
- **Description** : Allows you to log in as a guest user without having to create an account.
- **Response (success)** :
  ```json
  {
    "access": "str",
    "refresh": "str"
  }
  ```
- **Response codes**
    - `201 Ressource Created`

## Refresh token
```
🔒 POST https://localhost:4443/api/auth/refresh/
```
- **Description** : Allows you to obtain a new `access` token using a valid `refresh` token.
- **Body (JSON)** :
  ```json
  {
    "*refresh": "str"
  }
  ```
- **Response (success)** :
  ```json
  {
    "access": "str"
  }
  ```

## Guest register
```
🔒 PUT https://localhost:4443/api/auth/register/guest/
```
- **Description** : Enables you to register a guest user.
- **Body (JSON)** :
  ```json
  {
    "*username": "str",
    "*password": "str"
  }
  ```
- **Response (success)** :
  ```json
  {
    "*access": "str",
    "*refresh": "str"
  }
  ```

## Register
```
POST https://localhost:4443/api/auth/register/
```
- **Description** : Create a new user.
- **Body (JSON)** :
  ```json
  {
    "*username": "str",
    "*password": "str"
  }
  ```
- **Response (success)** :
  ```json
  {
    "*access": "str",
    "*refresh": "str"
  }
  ```

# 401
When a **401 error** is raised, the response contains a `code` field in addition to the `detail` field to identify the reasons for the authentication error. Here are all the possible codes:
- *not_authenticated*: when the token is missing.
- *incorrect_password*: when the password is incorrect.
- user_not_found*: when the token does not correspond to any user.
- *authentication_failed*: when authentication fails.
- sse_connection_required*: on some endpoints, sse connection is required.
- password_confirmation_required*: on some endpoints, password confirmation is required.
- token_not_valid*: when token is invalid.


# Chat

### Base URL
```
https://localhost:4443/api/chat/
```

## Chats
```
🔒 GET https://localhost:4443/api/chat/
```
- **Description** : Retrieves a list of all the user's conversations. If `q` is not set or has no value, this retrieves only the conversations that the user sees, i.e. conversations with which the `view_chat` field is equal to `True`. If `q` has a value, this filters the list of all conversations, keeping only those users whose name contains `q`.
- **Body (JSON)** :
  ```json
  {
    "q": "str"
  }
  ```
- **Response (success)** :
  - results:
  ```json
  {
    "id": 56,
    "chat_with": "SmallUserInstance",
    "last_message": "MessageInstance",
    "created_at": "datetime",
    "view_chat": "bool"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`

```
🔒 POST https://localhost:4443/api/chat/
```
- **Description** : Create a new chat instance with the user passed in the body.
- **Body (JSON)** :
  ```json
  {
    "*username": "str"
  }
  ```
- **Response (success)** :
  ```json
  {
    "id": 59,
    "chat_with": "SmallUserInstance",
    "last_message": "None",
    "created_at": "datetime",
    "view_chat": "bool"
  }
  ```
- **Response codes** :
  - `201 Created`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user who received the request has blocked conversation requests. If the user entered is the same as the user making the request. If the user making the request has blocked the specified user.
  - `404 Not Found` : The user entered has not been found: either because the user does not exist, or because the user entered is a guest user, or because the user who received the request has blocked the user who sent it.
  - `409 Conflict`: The conversation instance already exists between the two users.

## Chat
```
🔒 GET https://localhost:4443/api/chat/<int:chat_id>/
```
- **Description** : Retrieves the conversation instance with the `chat_id` passed in the request endpoint.
- **Response (success)** :
  ```json
  {
    "id": 69,
    "chat_with": "SmallUserInstance",
    "last_message": "MessageInstance",
    "created_at": "datetime",
    "view_chat": "bool",
    "unread_messages": "int"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user requests a `chat_id` to which he does not belong, or if the `chat_id` does not exist.

```
🔒 DELETE https://localhost:4443/api/chat/<int:chat_id>/
```
- **Description** : Changes the `view_chat` field of the conversation user instance. It is set to `False`. The conversation instance is not deleted.
- **Response codes** :
  - `204 No Content`
  - `403 Permission Denied` : If the user deletes a `chat_id` to which he doesn't belong, or when the `chat_id` doesn't exist.

## Messages
```
🔒 GET https://localhost:4443/api/chat/<int:chat_id>/messages/
```
- **Description** : Retrieves a list of all messages in the conversation instance.
- **Response (success)** :
  - results
  ```json
  {
    "id": "int",
    "chat_id": "int",
    "author": "SmallUserInstance",
    "content": "str",
    "sent_at": "datetime",
    "is_read": "bool"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user requests a `chat_id` to which he does not belong, or if the `chat_id` does not exist.

```
🔒 POST https://localhost:4443/api/<int:chat_id>/messages/
```
- **Description** : Create a message in the conversation instance.
- **Body (JSON)** :
  ```json
  {
    "*content": "str",
    "is_read": "bool"
  }
  ```
- **Response (success)** :
  - results:
  ```json
  {
    "id": "int",
    "chat_id": "int",
    "author": "SmallUserInstance",
    "content": "str",
    "sent_at": "datetime",
    "is_read": "bool"
  }
  ```
- **Response codes** :
  - `201 Created`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user requests a `chat_id` to which he does not belong, or if the `chat_id` does not exist.

# Game

### Base URL
```
https://localhost:4443/api/game/
```

## Matchs
```
🔒 GET https://localhost:4443/api/game/matches/<int:user_id>/
```
- **Description** : Retrieves a list of all the user's matches.
- **Response (success)** :
  - results:
  ```json
  {
    "id": "int",
    "code": "str",
    "game_mode": "str",
    "game_duration": "duration",
    "tournament_id": "int | None",
    "tournament_stage_id": "int | None",
    "tournament_n": "int | None"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`

## Tournois
```
🔒 GET https://localhost:4443/api/game/tournaments/<int:tournament_id>/
```
- **Description** : Retrieve a tournament instance.
- **Response (success)** :
```json
{
    "id": "int",
    "name": "str",
    "start_at": "datetime",
    "size": "int",
    "created_at": "datetime",
    "created_by": "int",
    "matches": {
        "round-of-16": ["MatchInstance", "MatchInstance", "..."],
        "quarter-final": ["..."],
        "semi-final": ["..."],
        "final": ["..."]
    }
}
```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`

## Jouer
```
🔒 POST https://localhost:4443/api/play/duel/
```
- **Description** : Allows a user to join the queue to play the `duel` game mode.
- **Response (success)** :
  ```json
  {
    "id": "int",
    "game_mode": "duel",
    "trophies": "int",
    "join_at": "datetime"
  }
  ```
- **Response codes** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `409 Conflict` : If the user is already playing a game.

```
🔒 POST https://localhost:4443/api/play/ranked/
```
- **Description** : Allows a user to join the queue to play the `ranked` game mode.
- **Response (success)** :
  ```json
  {
    "id": "int",
    "game_mode": "ranked",
    "trophies": "int",
    "join_at": "datetime"
  }
  ```
- **Response codes** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user is a guest.
  - `409 Conflict` : If the user is already playing a game.

## Lobby
```
🔒 POST https://localhost:4443/api/play/lobby/
```
- **Description** : Create a lobby.
- **Body (JSON)** :
  ```json
  {
    "*game_mode": "clash | custom_game"
  }
  ```
- **Response (success)** :
  ```json
  {
    "id": "int",
    "participants": ["LobbyParticipantInstance", "..."],
    "is_full": "bool",
    "code": "str",
    "max_participants": "int",
    "created_at": "datetime",
    "game_mode": "clash | custom_game",
    "match_type": "1v1 | 3v3"
  }
  ```
- **Response codes** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `409 Conflict` : If the user is already playing a game.

```
🔒 GET https://localhost:4443/api/play/lobby/
```
- **Description** : Retrieve the joined lobby instance.
- **Response (success)** :
  ```json
  {
    "id": "int",
    "participants": ["LobbyParticipantInstance", "..."],
    "is_full": "bool",
    "code": "str",
    "max_participants": "int",
    "created_at": "datetime",
    "game_mode": "clash | custom_game",
    "match_type": "1v1 | 3v3"
  }
  ```
- **Response codes** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `404 Not Found` : If the user does not belong to a lobby.

```
🔒 PATCH https://localhost:4443/api/play/lobby/
```
- **Description** : Updates the lobby instance.
- **Body (JSON)** :
  ```json
  {
    "match_type": "1v1 | 3v3"
  }
  ```
- **Response (success)** :
  ```json
  {
    "id": "int",
    "participants": ["LobbyParticipantInstance", "..."],
    "is_full": "bool",
    "code": "str",
    "max_participants": "int",
    "created_at": "datetime",
    "game_mode": "clash | custom_game",
    "match_type": "1v1 | 3v3"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user is not the lobby creator.
  - `404 Not Found` : If the user has not joined a lobby.
  - `405 Method Not Allowed` : If the lobby game mode is `clash`.

```
🔒 POST https://localhost:4443/api/play/lobby/<str:lobby_code>/
```
- **Description** : Join the lobby.
- **Response (success)** :
  ```json
  {
    "**": "SmallUserInstance",
    "creator": "bool",
    "team": "a | b | spectator",
    "join_at": "datetime",
    "is_ready": "bool"
  }
  ```
  - The `team` field is returned only if the game mode is `custom_game`.
- **Response codes** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `404 Not Found` : If the `lobby_code` does not exist or the lobby creator has blocked the user making the request.
  - `409 Conflict` : If the user is already playing a game.

```
🔒 PATCH https://localhost:4443/api/play/lobby/<str:lobby_code>/
```
- **Description** : Updates the user's instance in the lobby.
- **Body (JSON)** :
  ```json
  {
    "is_ready": "bool",
    "team": "a | b | spectator"
  }
  ```
  - The `team` field can only be passed if the game mode is `custom_game`.
- **Response (success)** :
  ```json
  {
    "**": "SmallUserInstance",
    "creator": "bool",
    "team": "a | b | spectator",
    "join_at": "datetime",
    "is_ready": "bool"
  }
  ```
  - The `team` field is returned only if the game mode is `custom_game`.
- **Response codes** :
  - `200 OK`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user has not joined the lobby, or if the player tries to join a team that is full.

### Ban
```
🔒 DELETE https://localhost:4443/api/play/lobby/<str:lobby_code>/ban/<int:user_id>/
```
- **Description** : Leave the lobby.
- **Response codes** :
  - `204 No Content`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user has not joined the lobby.


### Invitation
```
🔒 POST https://localhost:4443/api/play/lobby/<str:lobby_code>/invite/<int:user_id>/
```
- **Description** : Invites the user to the lobby.
- **Response codes** :
  - `204 No Content`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user has not joined the lobby, or the lobby does not exist, or the user tries to invite himself, or the user is not the creator of the lobby.
  - `404 Not Found` : If the guest user is not in the lobby.

### Lobby message
```
🔒 POST https://localhost:4443/api/play/lobby/<str:lobby_code>/message/
```
- **Description** : Send a message to the lobby.
- **Body (JSON)** :
  ```json
  {
    "*content": "str"
  }
  ```
- **Response codes** :
  - `201 Content Created`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user has not joined the lobby or the lobby does not exist.

## Tournament
```
🔒 POST https://localhost:4443/api/play/tournament/
```
- **Description** : Create a tournament.
- **Body (JSON)** :
  ```json
  {
    "*name": "str",
    "*size": "4 | 8 | 16",
    "private": "bool"
  }
  ```
- **Response (success)** :
  ```json
  {
    "id": "int",
    "name": "str",
    "participants": ["TournamentParticipantInstance", "..."],
    "private": "bool",
    "is_started": "bool",
    "start_at": "datetime",
    "code": "str",
    "size": "int",
    "created_at": "datetime",
    "created_by": "int"
  }
  ```
- **Response codes** :
  - `201 Ressource Created`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : The user has already created a tournament.
  - `409 Conflict` : If the user is already playing a game.

```
🔒 GET https://localhost:4443/api/play/tournament/
```
- **Description** : Returns the joined tournament instance.
  ```json
  {
    "id": "int",
    "name": "str",
    "participants": ["TournamentParticipantInstance", "..."],
    "private": "bool",
    "is_started": "bool",
    "start_at": "datetime",
    "code": "str",
    "size": "int",
    "created_at": "datetime",
    "created_by": "int",
    "matches": {
        "round-of-16": ["MatchInstance", "MatchInstance", "..."],
        "quarter-final": ["..."],
        "semi-final": ["..."],
        "final": ["..."]
    }
  }
  ```
  - The `matches` field is returned only if the tournament has started.
- **Response codes** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `404 Not Found` : - The `matches` field is returned only if the tournament has started.

```
🔒 POST https://localhost:4443/api/play/tournament/<str:tournament_code>/
```
- **Description** : Join the tournament.
- **Response (success)** :
  ```json
  {
    "**": "SmallUserInstance",
    "tournament": "int",
    "stage": "int",
    "seed": "int",
    "still_in": "bool",
    "creator": "bool",
    "join_at": "datetime"
  }
  ```
- **Response codes** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `404 Not Found` : If the tournament does not exist or the tournament creator has blocked the user making the request.
  - `409 Conflict` : If the user is already playing a game.

```
🔒 DELETE https://localhost:4443/api/play/tournament/<str:tournament_code>/
```
- **Description** : Leave the tournament.
- **Response codes** :
  - `204 No Content`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user has not joined the tournament.

### Banning
```
🔒 DELETE https://localhost:4443/api/play/tournament/<str:tournament_code>/ban/<int:user_id>/
```
- **Description** : Ban the tournament user.
- **Response codes** :
  - `204 No Content`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user has not joined the tournament, if the tournament does not exist, if the user tries to ban himself or if the user is not the creator of the tournament.
  - `404 Not Found` : If the guest user is not in the tournament.

### Invites
```
🔒 POST https://localhost:4443/api/play/tournament/<str:tournament_code>/invite/<int:user_id>/
```
- **Description** : Invites the user to the tournament.
- **Response codes** :
  - `204 No Content`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user has not joined the tournament, if the tournament does not exist, if the user tries to ban himself or if the user is not the creator of the tournament.
  - `404 Not Found` : If the guest user is not in the tournament.

### Tournament message
```
🔒 POST https://localhost:4443/api/play/tournament/<str:tournament_code>/message/
```
- **Description** : Send a message to the tournament.
- **Body (JSON)** :
  ```json
  {
    "*content": "str"
  }
  ```
- **Response codes** :
  - `201 Content Created`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user has not joined the tournament or the tournament does not exist.

### Search tournament
```
🔒 GET https://localhost:4443/api/play/tournament/search/
```
- **Description** : Search for a tournament. Displays public tournaments only.
- **Body (JSON)** :
  ```json
  {
    "*q": "str"
  }
  ```
- **Response (success)** :
  - results:
  ```json
  {
    "id": "int",
    "code": "str",
    "name": "str",
    "n_participants": "int",
    "size": "int",
    "created_by": "str"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`

# Users
### Base URL
```
https://localhost:4443/api/users/
```

## Me
```
🔒 GET https://localhost:4443/api/users/me/
```
- **Description** : Recovers the instance of the authenticated user.
- **Response (success)** :
  ```json
  {
    "id": "int",
    "username": "str",
    "is_guest": "bool",
    "created_at": "datetime",
    "profile_picture": "SmallProfilePictureInstance",
    "accept_friend_request": "bool",
    "accept_chat_from": "none | friends_only | everyone",
    "trophies": "int",
    "notifications": {"friend_requests":  0, "chats": 0},
    "is_online": "bool",
    "last_online": "datetime"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`

```
🔒 PATCH https://localhost:4443/api/users/me/
```
- **Description** : Updates the authenticated user's instance.
- **Body (JSON)** :
  ```json
  {
    "username": "str",
    "password": "str",
    "old_password": "str",
    "accept_friend_request": "bool",
    "accept_chat_from": "none | friends_only | everyone"
  }
  ```
  - The `old_password` field is required to change the password.
- **Response (success)** :
  ```json
  {
    "id": "int",
    "username": "str",
    "is_guest": "bool",
    "created_at": "datetime",
    "profile_picture": "SmallProfilePictureInstance",
    "accept_friend_request": "bool",
    "accept_chat_from": "none | friends_only | everyone",
    "trophies": "int",
    "notifications": {"friend_requests":  0, "chats": 0},
    "is_online": "bool",
    "last_online": "datetime"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `400 Bad Request`
  - `401 Unauthorized`

```
🔒 DELETE https://localhost:4443/api/users/me/
```
- **Description** : Deletes the instance of the authenticated user.
- **Body (JSON)** :
  ```json
  {
    "*password": "str"
  }
  ```
- **Response codes** :
  - `204 No Content`
  - `401 Unauthorized`

## User
```
🔒 GET https://localhost:4443/api/users/<int:user_id>/
```
- **Description** : Retrieve the user's instance.
- **Response (success)** :
  ```json
  {
    "id": "int",
    "username": "str",
    "is_guest": "bool",
    "profile_picture": "SmallProfilePictureInstance",
    "status": {"is_online": "bool", "game_playing":  "str | None", "last_online": "datetime"},
    "trophies": "int",
    "friends": "FriendsInstance | None"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`
  - `404 Not Found` : The user was not found: because it doesn't exist, or because the user was trying to block the requesting user.

## Friend requests
```
🔒 GET https://localhost:4443/api/users/me/friend_requests/
```
- **Description** : Retrieves a list of all the user's friend requests.
- **Response (success)** :
  - results:
  ```json
  {
    "id": "int",
    "sender": "SmallUserInstance",
    "receiver": "SmallUserInstance",
    "send_at": "datetime"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`

```
🔒 POST https://localhost:4443/api/users/me/friend_requests/
```
- **Description** : Sends a friend request to the user.
- **Body (JSON)** :
  ```json
  {
    "*username": "str"
  }
  ```
- **Response (success)** :
  ```json
  {
    "id": "int",
    "sender": "SmallUserInstance",
    "receiver": "SmallUserInstance",
    "send_at": "datetime"
  }
  ```
- **Response codes** :
  - `201 Ressource Created`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user makes a friend request to a user he has blocked, or the user does not receive friend requests, or the user making the request has sent more than 20 pending requests.
  - `404 Not Found` : If the username does not exist or has blocked the user making the request.
  - `409 Conflict` : The request for friends or friendship already exists.

```
🔒 GET https://localhost:4443/api/users/me/friend_requests/received/
```
- **Description** : Retrieves a list of all friend requests received.
- **Response (success)** :
  - results:
  ```json
  {
    "id": "int",
    "sender": "SmallUserInstance",
    "receiver": "SmallUserInstance",
    "send_at": "datetime"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`

## Friend request
```
🔒 GET https://localhost:4443/api/users/me/friend_requests/<int:friends_request_id>/
```
- **Description** : Retrieves a friend request instance.
- **Response (success)** :
  - results:
  ```json
  {
    "id": "int",
    "sender": "SmallUserInstance",
    "receiver": "SmallUserInstance",
    "send_at": "datetime"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`
  - `404 Not Found` : If the user does not exist, or if the user trying to access the friend request instance is neither the one who sent it, nor the one who received it.

```
🔒 DELETE https://localhost:4443/api/users/me/friend_requests/<int:friends_request_id>/
```
- **Description** :  Deletes the friend request instance.
- **Response codes** :
  - `204 No Content`
  - `401 Unauthorized`
  - `404 Not Found` : If the user does not exist, or if the user trying to access the friend request instance is neither the one who sent it, nor the one who received it.

```
🔒 POST https://localhost:4443/api/users/me/friend_requests/<int:friends_request_id>/
```
- **Description** : Accept a friend request.
- **Response (success)** :
  - results:
  ```json
  {
    "id": "int",
    "friend": "SmallUserInstance",
    "friend_wins": "int",
    "me_wins": "int",
    "friends_since": "datetime",
    "matches_played_against": "int",
    "matches_played_together": "int",
    "matches_won_together": "int"
  }
  ```
- **Response codes** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user who sent the request tries to accept it himself
  - `404 Not Found` : If the user does not exist, or if the user trying to access the friend request instance is neither the one who sent it, nor the one who received it.

## Friends
```
🔒 GET https://localhost:4443/api/users/me/friends/
```
- **Description** : Retrieves a list of all the user's friendships.
- **Response (success)** :
  - results:
  ```json
  {
    "id": "int",
    "friend": "SmallUserInstance",
    "friend_wins": "int",
    "me_wins": "int",
    "friends_since": "datetime",
    "matches_played_against": "int",
    "matches_played_together": "int",
    "matches_won_together": "int"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`

```
🔒 DELETE https://localhost:4443/api/users/me/friends/<int:friends_id>/
```
- **Description** : Deletes a friendship.
- **Response codes** :
  - `204 No Content`
  - `401 Unauthorized`
  - `404 Not Found` : If the friendship doesn't exist or the person making the request isn't part of the friendship

## Blocked
```
🔒 GET https://localhost:4443/api/users/me/blocked/
```
- **Description** : Retrieves a list of all blocked users.
- **Response (success)** :
  - results:
  ```json
  {
    "id": "int",
    "blocked": "SmallUserInstance",
    "blocked_at": "datetime"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`

```
🔒 POST https://localhost:4443/api/users/me/blocked/
```
- **Description** : Blocks a user.
- **Body (JSON)** :
  ```json
  {
    "*user_id": "int"
  }
  ```
- **Response (success)** :
  - results:
  ```json
  {
    "id": "int",
    "blocked": "SmallUserInstance",
    "blocked_at": "datetime"
  }
  ```
- **Response codes** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `403 Permission Denied` : If the user tries to block himself or has already blocked 50 users.
  - `404 Not Found` : If the user does not exist, or the user is a guest user, or the user has already blocked the user making the request.
  - `409 Conflict` : If the user has already blocked user_id.

```
🔒 DELETE https://localhost:4443/api/users/me/blocked/<int:blocked_id>/
```
- **Description** : If the user has already blocked user_id.
- **Response codes** :
  - `204 No Content`
  - `401 Unauthorized`
  - `404 Not Found` : If blocked_id does not exist or the user making the request is not the same user who blocked the user in blocked_id.

## User data
```
🔒 GET https://localhost:4443/api/users/me/download-data/
```
- **Description** : Retrieves a .json file with all user data.
- **Réponse (contenu du fichier json)** :
  ```json
  {
    "user_data": "UserMeInstance",
    "profile_pictures_data": "list[ProfilePictureInstance]",
    "friends_data": {"friends": "list[FriendInstance]", "friend_requests_sent": "list[FriendRequestsInstance]", "friend_requests_received": "list[FriendRequestsInstance]", "blocked_users": "list[BlockedInstance]"},
    "stats_data": "list[StatsInstance]",
    "chat_data": "list[ChatInstance]",
    "game_data": {"matches": "list[MatchInstance]", "tournament": "list[TournamentInstance]"}
  }
  ```
  - In `ChatInstance` the `last_message` field is replaced by the `messages` field, which is a list of all the messages in the conversation.
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`

## Profile pictures
```
🔒 GET https://localhost:4443/api/users/profile-pictures/
```
- **Description** : Retrieves a list of all available profile photos.
- **Réponse** :
  ```json
  {
    "id": "int",
    "name": "str",
    "unlock_reason": "str",
    "unlock": "bool",
    "is_equiped": "bool",
    "url": "/assets/profile_pictures/xxx.png",
    "small": "/assets/profile_pictures/xxx_small.png",
    "medium": "/assets/profile_pictures/xxx_medium.png",
    "large": "/assets/profile_pictures/xxx_large.png"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`

```
🔒 PUT https://localhost:4443/api/users/profile-picture/<int:id>/
```
- **Description** : Update the user's profile photo.
- **Réponse** :
  ```json
  {
    "id": "int",
    "name": "str",
    "unlock_reason": "str",
    "unlock": "bool",
    "is_equiped": "bool",
    "url": "/assets/profile_pictures/xxx.png",
    "small": "/assets/profile_pictures/xxx_small.png",
    "medium": "/assets/profile_pictures/xxx_medium.png",
    "large": "/assets/profile_pictures/xxx_large.png"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`
  - `403 Permission Denied` : The user did not unlock the profile photo.
  - `404 Not Found` : The profile photo doesn't exist.

## Stats
```
🔒 GET https://localhost:4443/api/users/me/stats/
```
- **Description** : Retrieves a list of statistics for all game modes. There are no statistics for the `custom_game` game mode. There are statistics for the `global` game mode. This corresponds to the player's statistics for all game modes. The `global` instance is always at index 0. Although the data returned is in list form, this endpoint has no pagination system, the number of results being fixed.
- **Response (success)** :
  ```json
  {
    "id": "int",
    "game_mode": "global | duel | clash | ranked | tournament",
    "game_played": "int",
    "wins": "int",
    "scored": "int",
    "longest_win_streak": "int",
    "current_win_streak": "int",
    "own_goals": "int",
    "tournament_wins": "int"
  }
  ```
  - The `own_goals` field is returned only if the game mode is `clash`.
  - The `tournament_wins` field is returned only if the game mode is `tournament`.
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`

## Ranked stats
```
🔒 GET https://localhost:4443/api/users/me/stats/ranked/
```
- **Description** : Retrieves a list of the evolution of the number of trophies over the course of matches.
- **Response (success)** :
  - results:
  ```json
  {
    "id": "int",
    "trophies": "int",
    "total_trophies": "int",
    "at": "datetime"
  }
  ```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`


# SSE

```
🔒 GET https://localhost:4443/sse/users/
```
- **Description** :  Allows you to connect to the SSE.
- **Response (success)** :
  - results:
```
event: event_name\n
data: {data}\n\n
```
- **Response codes** :
  - `200 OK`
  - `401 Unauthorized`

# Event SSE
```
🔒 GET https://localhost:4443/api/private/users/
```
- **Description** : Creates an SSE event.
- **Body (JSON)** :
  ```json
  {
    "*users_id": "list[int]",
    "*event_code": "str",
    "data": "dict | None",
    "kwargs": "dict | None"
  }
  ```
  - **Response (success)** :
  {
    "*users_id": "list[int]",
    "*event_code": "str",
    "data": "dict | None",
    "kwargs": "dict | None"
  }
- **Response codes** :
  - `201 Ressource Created`
  - `400 Bad Request`
  - `404 Not Found` : If none of the users sent exist, or if none of the users sent are logged in.

## Message
- ***receive-message*** is sent when the user receives a message. data: *MessageInstance*, kwargs : *username, message, chat_id*

## User
- ***delete-user*** is sent when the user deletes his account.
- 
## Game
Event sent when the player plays in a game:
- ***game-start*** is sent to all users of the game. data: *MatchInstance*

## Friend
Events sent for friendship management:
- ***accept-friend-request*** is sent to the user making the friend request, if ever logged in. It is sent if the user receiving the request accepts the request. data: *FriendInstance*, kwargs : *username*
- ***receive-friend-request*** is sent to the user receiving the friend request, if ever logged in. It is sent if the user receives a friend request. data: *FriendRequestInstance*, kwargs : *id, username*- ***reject-friend-request*** est envoyé à l'utilisateur faisant la demande d'amis, si jamais il est connecté. Il est envoyé si jamais l'utilisateur recevant la demande rejette la demande, si l'utilisateur recevant la demande bloque celui l'envoyant, ou si l'utilisateur recevant la demande supprime son compte. data: *{"id" : FriendRequestInstance.id}*
- ***cancel-friend-request*** is sent to the user receiving the friend request, if ever logged in. It is sent if the user sending the friend request cancels the friend request, if the user sending the friend request blocks the user receiving it *(only in this case, the event is sent to both users)*, or if the user sending the friend request deletes his account. data: *{“id” : FriendRequestInstance.id}*- ***delete-friend*** est envoyé à l'autre utilisateur de la relation d'amitié, si jamais il est connecté. Il est envoyé si jamais un des utilisateurs supprime l'amitié, si l'un des deux utilisateurs bloque l'autre, ou si l'un des deux utilisateurs supprime son compte. data: *{"id" : FriendInstance.id}*

## Lobby
Events sent when the user is in a lobby:
- ***lobby-join*** is sent to all users already in the lobby to inform them that a new user has joined the lobby. data: *LobbyParticipantInstance*, kwargs : *username*
- ***lobby-leave*** is sent to all users in the lobby to inform them that a user has left the lobby. data: *{“id” : “int”}*, kwargs : *username*
- ***lobby-banned*** is sent to the banned user. Other lobby participants receive a *lobby-leave* event.
- ***lobby-message***is sent is sent to all users present in the lobby (except the author of the message). kwargs: *username* is sent.
- ***lobby-update*** is sent to all users present in the lobby (except the creator) to inform them that lobby parameters have been changed. data: *LobbyInstance* (only fields that have been modified).
- ***lobby-update-participant*** est envoyé à tous les utilisateurs présents dans le lobby (excepté celui qui performe la modification) afin de les informer que les paramètres de l'utilisateur ont été changés. data: *LobbyParticipantInstance* (uniquement les champs qui ont été modifiés à savoir où `creator`, `team` ou `is_ready`).
- ***lobby-spectate-game*** is sent to all users in the “spectator” team when a game starts. data : *{“code” : “str”}*
- ***lobby-destroy*** is sent to all guest users present in the lobby in the event that the creator leaves the lobby, and no more registered users remain in the lobby, to inform them that the lobby has been destroyed.

## Tournament
Events sent when the user is in a tournament:
- ***tournament-join*** is sent to all users already in the tournament to inform them that a new user has joined the tournament. data: *TournamentParticipantInstance*, kwargs : *username*
- ***tournament-leave*** is sent to all users present in the tournament to inform them that a user has left the tournament. data: *{“id” : “int”}*, kwargs : *username*
- ***tournament-banned*** is sent to the banned user. Other tournament participants receive a *tournament-leave* event.
- ***tournament-message***is sent is sent to all users present in the tournament (except the author of the message). kwargs: *username*
- ***tournament-start-at*** is sent to all tournament participants to inform them that the tournament starts at “start_at”. This is when the tournament is 80% full. There is then a 20-second waiting period before the tournament starts. If someone leaves during this waiting time, the *tournament-start-cancel* event is sent to all users still present and “start_at” is reset to None. data: *{“id” : “int”, “start_at” : “datetime”}*
- ***tournament-start-cancel*** is sent to all tournament participants to inform them that the tournament start has been cancelled. data: *{“id” : “int”, “start_at” : “datetime”}*
- ***tournament-start*** is sent to all tournament participants to inform them that the tournament is starting (either because the “start_at” has passed or because the tournament is full). There is then a three-second timer before the game starts, to allow time to see the bracket (which is sent in the data). data: *TournamentInstance*
- ***tournament-available-spectate-matches*** is sent to all participants of the eliminated tournament so that they can watch the remaining matches as spectators. data: *{“game_id” : “game_code”, ...}*
- ***tournament-match-finish*** is sent to all tournament participants to inform them of the result of a match. data: *TournamentInstance*, kwargs : *winner, looser, score_winner, score_looser, finish_reason*
- ***tournament-finish*** is sent to all tournament participants to inform them that the tournament is finished. kwargs: *id, name, username*
- 
## Invites
Event sent when a player invites another player to a lobby or tournament:
- ***invite-clash*** is sent to the user to join a lobby clash. data : *{“id” : “int”, “code” : “str”}*, kwargs : *username, code*
- ***invite-1v1*** is sent to the user to join a game_custom in 1v1. data: *{“id”: “int”, “code”: “str”}*, kwargs: *username, code*
- ***invite-3v3*** is sent to the user to join a game_custom in 3v3. data : *{“id” : “int”, “code” : “str”}*, kwargs : *username, code*
- ***invite-tournament*** is sent to the user to join a tournament. data : *{“id” : “int”, “code” : “str”}*, kwargs : *username, code*
In target is sent the URL to put in the browser if the user accepts the invitation.

## User
- ***user-delete*** is sent to the user who is deleting his data. For example, if several customers are logged in, one of them deletes his account, the other customers know about it and can delog the user.
- ***profile-picture-unlocked*** is sent to the user who unlocks a profile picture. data : *ProfilePictureInstance*, kwargs : *id*, taget : *use, see all*
