# Documentation de l'API


### Base de l'URL
```
https://localhost:4443/api/
```


## Authentification
L'API utilise un système d'authentification basé sur **JSON Web Tokens (JWT)**.

### Obtention d'un token
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
- **Réponse (succès)** :
  ```json
  {
    "access": "str",
    "refresh": "str"
  }
  ```

### Utilisation du token
Pour accéder aux endpoints protégés, ajoutez le token dans l'en-tête `Authorization` :
```
Authorization: Bearer <access_token>
```

### Endpoints avec authentification
Tous les endpoints marqués avec 🔒 nécessitent une authentification. Ces endpoints correspondent aux requêtes qui communiquent avec le front (c'est l'API public).

### Codes de réponse
- `200 OK` : Requête réussie.
- `201 Created` : Ressource créée.
- `204 No Content` : Requête réussie sans return de body (souvent utilisé lors de la suppression d'un élément).
- `400 Bad Request` : Erreur de validation.
- `401 Unauthorized` : Authentification requise.
- `403 Permission Denied` : Le client n'a pas les droits d'accès au contenu (contrairement à 401, l'identité du client est connue du serveur.)
- `404 Not Found` : Ressource introuvable.
- `405 Method Not Allowed` : Méthode de requête non autorisée.
- `409 Conflict` : Conflit lors de la requête (souvent lorsque le client tente de créer une ressource qui existe déjà).
- `415 Unsupported Media Type` : Le format du *content-type* demandé n'est pas pris en charge par le serveur.
- `429 Throttled` : Toutes les requêtes **POST**, **PUT** et **PATCH** peuvent renvoyer cette erreur. Cela arrive quand beaucoup de requêtes sont envoyées strictement au même moment. Le détail de l'erreur est toujours le même : *"Request was throttled."*
- `500 Internal Server Error` : Erreur côté serveur.
- `502 Bad Gateway` : Cette réponse d'erreur signifie que le serveur a reçu une réponse non valide.
- `503 Service Unavailable` : Le serveur n'est pas prêt à traiter la demande (dans notre cas, parce qu'un micro service autre que celui de la requête ne fonctionne plus).

## Pagination

L'API utilise un système de pagination basé sur les paramètres **`limit`** et **`offset`** pour gérer efficacement les réponses nombreuses.

- **`limit`** : Définit le nombre maximum d'éléments à retourner dans une réponse.
    - Par défaut : `20` (si non spécifié).
    - Exemple : `?limit=50` retournera un maximum de 50 éléments.

- **`offset`** : Définit le point de départ des éléments à inclure dans la réponse.
    - Par défaut : `0` (si non spécifié).
    - Exemple : `?offset=40` commencera à retourner les éléments à partir du 41ᵉ.

### Exemple
Si l'API contient 100 éléments :
- Une requête avec `?limit=10&offset=20` retourn les éléments de l'index 21 à 30.

### Réponse typique avec pagination
```json
{
  "count": "int",
  "next": "https://localhost:4443/api/resource/?limit=10&offset=30",
  "previous": "https://localhost:4443/api/resource/?limit=10&offset=10",
  "results": []
}
```
- ***count*** : Nombre total d'éléments
- ***next*** : URL de la page suivante
- ***previous*** : URL de la page précédente
- ***results*** : Liste des éléments paginés

Les champs **`next`** et **`previous`** peuvent être égaux à `null` s'il n'existe pas de lien vers une page suivante ou précédente.

### Body
Tous les champs précédés d'un `*` sont exigés.
Les types dans les champs correspondent au type utilisé en _python_.
Lorsqu'un champ peut être renseigné dans une requête `GET`, il doit être renseigné dans l'URL de la requête sous la forme : `url/?nom_du_champ=valaeur_du_champ`.


# Auth

### Base URL
```
https://localhost:4443/api/auth/
```
## Connection

```
POST https://localhost:4443/api/auth/login/
```
- **Description** : Permet aux utilisateurs de se connecter en fournissant leurs identifiants.
- **Body (JSON)** :
  ```json
  {
    "*username": "str",
    "*password": "str"
  }
  ```
- **Réponse (succès)** :
  ```json
  {
    "access": "str",
    "refresh": "str"
  }
  ```
- **Codes de réponse** :
    - `200 OK`
    - `401 Unauthorized`

## Utilisateur invité
```
POST https://localhost:4443/api/auth/guest/
```
- **Description** : Permet de se connecter en tant qu'utilisateur invité sans avoir à créer de compte.
- **Réponse (succès)** :
  ```json
  {
    "access": "str",
    "refresh": "str"
  }
  ```
- **Codes de réponse**
    - `201 Ressource Created`

## Rafraîchissement du token
```
🔒 POST https://localhost:4443/api/auth/refresh/
```
- **Description** : Permet d'obtenir un nouveau token `access` à l'aide d'un token `refresh` valide.
- **Body (JSON)** :
  ```json
  {
    "*refresh": "str"
  }
  ```
- **Réponse (succès)** :
  ```json
  {
    "access": "str"
  }
  ```

## Enregistrement d'un utilisateur invité
```
🔒 PUT https://localhost:4443/api/auth/register/guest/
```
- **Description** : Permet d'enregistrer un utilisateur invité.
- **Body (JSON)** :
  ```json
  {
    "*username": "str",
    "*password": "str"
  }
  ```
- **Réponse (succès)** :
  ```json
  {
    "*access": "str",
    "*refresh": "str"
  }
  ```

## Enregistrement d'un nouvel utilisateur
```
POST https://localhost:4443/api/auth/register/
```
- **Description** : Permet de créer un nouvel utilisateur.
- **Body (JSON)** :
  ```json
  {
    "*username": "str",
    "*password": "str"
  }
  ```
- **Réponse (succès)** :
  ```json
  {
    "*access": "str",
    "*refresh": "str"
  }
  ```

# 401
Lorsqu'une **erreur 401** est levé, dans la réponse se trouve un champ `code` en plus du champ `detail` permettant d'identifier les raisons de l'erreur d'authentification. Voici tous les codes possibles :
- *not_authenticated* : lorsqu'il manque le token.
- *incorrect_password* : lorsque le mot de passe est incorrect.
- *user_not_found* : lorsque le token ne correspond à aucun utilisateur.
- *authentication_failed* : lorsque l'authentification échoue.
- *sse_connection_required* : sur certains endpoints, la connexion sse est requise.
- *password_confirmation_required* : sur certains endpoints, une confirmation du mot de passe est requise.
- *token_not_valid* : lorsque le token n'est pas valide.

# Chat

### Base URL
```
https://localhost:4443/api/chat/
```

## Conversations
```
🔒 GET https://localhost:4443/api/chat/
```
- **Description** : Récupère la liste de toutes les conversations de l'utilisateur. Si `q` n'est pas renseigné ou n'a pas de valeur, cela récupère uniquement les conversations que l'utilisateur voit, c'est-à-dire les conversations avec lesquelles le champ `view_chat` est egale à `True`. Si `q` a une valeur, cela filtre la liste de toutes les conversations en ne gardant que les utilisateurs dont le nom contient `q`.
- **Body (JSON)** :
  ```json
  {
    "q": "str"
  }
  ```
- **Réponse (succès)** :
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
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`

```
🔒 POST https://localhost:4443/api/chat/
```
- **Description** : Créer une nouvelle instance de chat avec l'utilisateur passé dans le body.
- **Body (JSON)** :
  ```json
  {
    "*username": "str"
  }
  ```
- **Réponse (succès)** :
  ```json
  {
    "id": 59,
    "chat_with": "SmallUserInstance",
    "last_message": "None",
    "created_at": "datetime",
    "view_chat": "bool"
  }
  ```
- **Codes de réponse** :
  - `201 Created`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur qui a reçu la demande a bloqué les demandes de conversation. Si l'utilisateur renseigné est le même que l'utilisateur qui fait la requête. Si l'utilisateur qui fait la requête a bloqué l'utilisateur renseigné.
  - `404 Not Found` : L'utilisateur renseigné n'a pas été trouvé : ou parce que l'utilisateur n'existe pas, ou parce que l'utilisateur renseigné est un utilisateur invité, ou parce que l'utilisateur qui a reçu la demande a bloqué celui qui l'a envoyée.
  - `409 Conflict` : L'instance de conversation existe déjà entre les deux utilisateurs.

## Conversation
```
🔒 GET https://localhost:4443/api/chat/<int:chat_id>/
```
- **Description** : Récupère l'instance de conversation avec le `chat_id` passé dans l'endpoint de la requête.
- **Réponse (succès)** :
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
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur demande un `chat_id` auquel il n'appartient pas ou alors que le `chat_id` n'existe pas.

```
🔒 DELETE https://localhost:4443/api/chat/<int:chat_id>/
```
- **Description** : Change le champ `view_chat` de l'instance de l'utilisateur de la conversation. Il est mis à `False`. L'instance de la conversation n'est pas supprimée.
- **Codes de réponse** :
  - `204 No Content`
  - `403 Permission Denied` : Si l'utilisateur supprime un `chat_id` auquel il n'appartient pas ou alors que le `chat_id` n'existe pas.

## Messages
```
🔒 GET https://localhost:4443/api/chat/<int:chat_id>/messages/
```
- **Description** : Récupère la liste de tous les messages de l'instance de la conversation.
- **Réponse (succès)** :
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
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur demande un `chat_id` auquel il n'appartient pas ou alors que le `chat_id` n'existe pas.

```
🔒 POST https://localhost:4443/api/<int:chat_id>/messages/
```
- **Description** : Créer un message dans l'instance de la conversation.
- **Body (JSON)** :
  ```json
  {
    "*content": "str",
    "is_read": "bool"
  }
  ```
- **Réponse (succès)** :
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
- **Codes de réponse** :
  - `201 Created`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur demande un `chat_id` auquel il n'appartient pas ou alors que le `chat_id` n'existe pas.

# Game

### Base URL
```
https://localhost:4443/api/game/
```

## Matchs
```
🔒 GET https://localhost:4443/api/game/matches/<int:user_id>/
```
- **Description** : Récupère la liste de tous les matchs de l'utilisateur.
- **Réponse (succès)** :
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
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`

## Tournois
```
🔒 GET https://localhost:4443/api/game/tournaments/<int:tournament_id>/
```
- **Description** : Récupère l'instance d'un tournoi.
- **Réponse (succès)** :
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
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`

## Jouer
```
🔒 POST https://localhost:4443/api/play/duel/
```
- **Description** : Permet à un utilisateur de rejoindre la file d'attente pour jouer à au mode de jeu `duel`.
- **Réponse (succès)** :
  ```json
  {
    "id": "int",
    "game_mode": "duel",
    "trophies": "int",
    "join_at": "datetime"
  }
  ```
- **Codes de réponse** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `409 Conflict` : Si l'utilisateur est déjà en train de jouer.

```
🔒 POST https://localhost:4443/api/play/ranked/
```
- **Description** : Permet à un utilisateur de rejoindre la file d'attente pour jouer à au mode de jeu `ranked`.
- **Réponse (succès)** :
  ```json
  {
    "id": "int",
    "game_mode": "ranked",
    "trophies": "int",
    "join_at": "datetime"
  }
  ```
- **Codes de réponse** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur est un utilisateur invité.
  - `409 Conflict` : Si l'utilisateur est déjà en train de jouer.

## Lobby
```
🔒 POST https://localhost:4443/api/play/lobby/
```
- **Description** : Créer un lobby.
- **Body (JSON)** :
  ```json
  {
    "*game_mode": "clash | custom_game"
  }
  ```
- **Réponse (succès)** :
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
- **Codes de réponse** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `409 Conflict` : Si l'utilisateur est déjà en train de jouer.

```
🔒 GET https://localhost:4443/api/play/lobby/
```
- **Description** : Retourne l'instance du lobby auquel l'utilisateur appartient.
- **Réponse (succès)** :
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
- **Codes de réponse** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `404 Not Found` : Si l'utilisateur n'appartient à aucun lobby.

```
🔒 PATCH https://localhost:4443/api/play/lobby/
```
- **Description** : Met à jour l'instance du lobby.
- **Body (JSON)** :
  ```json
  {
    "match_type": "1v1 | 3v3"
  }
  ```
- **Réponse (succès)** :
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
- **Codes de réponse** :
  - `200 OK`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur n'est pas le créateur du lobby.
  - `404 Not Found` : Si l'utilisateur n'a pas rejoint de lobby.
  - `405 Method Not Allowed` : Si le mode de jeu du lobby est `clash`.

```
🔒 POST https://localhost:4443/api/play/lobby/<str:lobby_code>/
```
- **Description** : Rejoins l'instance du lobby.
- **Réponse (succès)** :
  ```json
  {
    "**": "SmallUserInstance",
    "creator": "bool",
    "team": "a | b | spectator",
    "join_at": "datetime",
    "is_ready": "bool"
  }
  ```
  - Le champ `team` est renvoyé uniquement si le mode de jeu est `custom_game`.
- **Codes de réponse** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `404 Not Found` : Si le `lobby_code` n'existe pas ou que le créateur du lobby a bloqué l'utilisateur qui fait la requête.
  - `409 Conflict` : Si l'utilisateur est déjà en train de jouer.

```
🔒 PATCH https://localhost:4443/api/play/lobby/<str:lobby_code>/
```
- **Description** : Met à jour l'instance de l'utilisateur dans le lobby.
- **Body (JSON)** :
  ```json
  {
    "is_ready": "bool",
    "team": "a | b | spectator"
  }
  ```
  - Le champ `team` peut être passé uniquement si le mode de jeu est `custom_game`.
- **Réponse (succès)** :
  ```json
  {
    "**": "SmallUserInstance",
    "creator": "bool",
    "team": "a | b | spectator",
    "join_at": "datetime",
    "is_ready": "bool"
  }
  ```
  - Le champ `team` est renvoyé uniquement si le mode de jeu est `custom_game`.
- **Codes de réponse** :
  - `200 OK`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur n'a pas rejoint le lobby ou que le joueur tente de rejoindre une team qui est pleine.

### Ban
```
🔒 DELETE https://localhost:4443/api/play/lobby/<str:lobby_code>/ban/<int:user_id>/
```
- **Description** : Quitte le lobby.
- **Codes de réponse** :
  - `204 No Content`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur n'a pas rejoint le lobby.


### Invitation
```
🔒 POST https://localhost:4443/api/play/lobby/<str:lobby_code>/invite/<int:user_id>/
```
- **Description** : Invite l'utilisateur dans le lobby.
- **Codes de réponse** :
  - `204 No Content`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur n'a pas rejoint le lobby, ou que le lobby n'existe pas, que l'utilisateur tente de s'inviter lui-même ou que l'utilisateur n'est pas le créateur du lobby.
  - `404 Not Found` : Si l'utilisateur invité n'est pas dans le lobby.

### Message de lobby
```
🔒 POST https://localhost:4443/api/play/lobby/<str:lobby_code>/message/
```
- **Description** : Envoie un message dans le lobby.
- **Body (JSON)** :
  ```json
  {
    "*content": "str"
  }
  ```
- **Codes de réponse** :
  - `201 Content Created`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur n'a pas rejoint le lobby ou que le lobby n'existe pas.

## Tournoi
```
🔒 POST https://localhost:4443/api/play/tournament/
```
- **Description** : Créer un tournoi.
- **Body (JSON)** :
  ```json
  {
    "*name": "str",
    "*size": "4 | 8 | 16"
  }
  ```
- **Réponse (succès)** :
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
- **Codes de réponse** :
  - `201 Ressource Created`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : L'utilisateur a déjà créé un tournoi.
  - `409 Conflict` : Si l'utilisateur est déjà en train de jouer.

```
🔒 GET https://localhost:4443/api/play/tournament/
```
- **Description** : Retourne l'instance du tournoi auquel l'utilisateur appartient.
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
  - Le champ `matches` est renvoyé uniquement si le tournoi est commencé.
- **Codes de réponse** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `404 Not Found` : Si l'utilisateur n'appartient à aucun tournoi.

```
🔒 POST https://localhost:4443/api/play/tournament/<str:tournament_code>/
```
- **Description** : Rejoins l'instance du tournoi.
- **Réponse (succès)** :
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
- **Codes de réponse** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `404 Not Found` : Si le tournoi n'existe pas ou que le créateur du tournoi a bloqué l'utilisateur qui fait la requête.
  - `409 Conflict` : Si l'utilisateur est déjà en train de jouer.

```
🔒 DELETE https://localhost:4443/api/play/tournament/<str:tournament_code>/
```
- **Description** : Quitte le tournoi.
- **Codes de réponse** :
  - `204 No Content`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur n'a pas rejoint le tournoi.

### Ban
```
🔒 DELETE https://localhost:4443/api/play/tournament/<str:tournament_code>/ban/<int:user_id>/
```
- **Description** : Ban l'utilisateur du tournoi.
- **Codes de réponse** :
  - `204 No Content`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur n'a pas rejoint le tournoi, que le tournoi n'existe pas, que l'utilisateur tente de se bannir lui-même ou que l'utilisateur n'est pas le créateur du tournoi.
  - `404 Not Found` : Si l'utilisateur invité n'est pas dans le tournoi.

### Invitation
```
🔒 POST https://localhost:4443/api/play/tournament/<str:tournament_code>/invite/<int:user_id>/
```
- **Description** : Invite l'utilisateur dans le tournoi.
- **Codes de réponse** :
  - `204 No Content`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur n'a pas rejoint le tournoi, que le tournoi n'existe pas, que l'utilisateur tente de se bannir lui-même ou que l'utilisateur n'est pas le créateur du tournoi.
  - `404 Not Found` : Si l'utilisateur invité n'est pas dans le tournoi.

### Messages de tournoi
```
🔒 POST https://localhost:4443/api/play/tournament/<str:tournament_code>/message/
```
- **Description** : Envoie un message dans le tournoi.
- **Body (JSON)** :
  ```json
  {
    "*content": "str"
  }
  ```
- **Codes de réponse** :
  - `201 Content Created`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur n'a pas rejoint le tournoi ou que le tournoi n'existe pas.

### Chercher un tournoi
```
🔒 GET https://localhost:4443/api/play/tournament/search/
```
- **Description** : Recherche un tournoi. Affiche uniquement les tournois publics.
- **Body (JSON)** :
  ```json
  {
    "*q": "str"
  }
  ```
- **Réponse (succès)** :
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
- **Codes de réponse** :
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
- **Description** : Récupère l'instance de l'utilisateur authentifié.
- **Réponse (succès)** :
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
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`

```
🔒 PATCH https://localhost:4443/api/users/me/
```
- **Description** : Met à jour l'instance de l'utilisateur authentifié.
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
  - Le champ `old_password` est requis pour changer le mot de passe.
- **Réponse (succès)** :
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
- **Codes de réponse** :
  - `200 OK`
  - `400 Bad Request`
  - `401 Unauthorized`

```
🔒 DELETE https://localhost:4443/api/users/me/
```
- **Description** : Supprime l'instance de l'utilisateur authentifié.
- **Body (JSON)** :
  ```json
  {
    "*password": "str"
  }
  ```
- **Codes de réponse** :
  - `204 No Content`
  - `401 Unauthorized`

## Utilisateur
```
🔒 GET https://localhost:4443/api/users/<int:user_id>/
```
- **Description** : Récupère l'instance de l'utilisateur.
- **Réponse (succès)** :
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
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`
  - `404 Not Found` : L'utilisateur n'a pas été trouvé : parce qu'il n'existe pas, ou parce que l'utilisateur cherchait à bloquer l'utilisateur qui fait la requête.

## Demandes d'amis
```
🔒 GET https://localhost:4443/api/users/me/friend_requests/
```
- **Description** : Récupère la liste toutes les demandes d'amis de l'utilisateur.
- **Réponse (succès)** :
  - results:
  ```json
  {
    "id": "int",
    "sender": "SmallUserInstance",
    "receiver": "SmallUserInstance",
    "send_at": "datetime"
  }
  ```
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`

```
🔒 POST https://localhost:4443/api/users/me/friend_requests/
```
- **Description** : Envoie une demande d'ami à l'utilisateur.
- **Body (JSON)** :
  ```json
  {
    "*username": "str"
  }
  ```
- **Réponse (succès)** :
  ```json
  {
    "id": "int",
    "sender": "SmallUserInstance",
    "receiver": "SmallUserInstance",
    "send_at": "datetime"
  }
  ```
- **Codes de réponse** :
  - `201 Ressource Created`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l'utilisateur fait une demande d'amis à un utilisateur qu'il a bloqué, ou que l'utilisateur ne reçoit pas les demandes d'amis, ou que l'utilisateur qui fait la demande a envoyé plus de 20 demandes en attente.
  - `404 Not Found` : Si le nom d'utilisateur n'existe pas ou qu'il a bloqué l'utilisateur qui fait la requête.
  - `409 Conflict` : La demande d'amis ou l'amitié existe déjà.

```
🔒 GET https://localhost:4443/api/users/me/friend_requests/received/
```
- **Description** : Récupère la liste de toutes les demandes d'ami reçu.
- **Réponse (succès)** :
  - results:
  ```json
  {
    "id": "int",
    "sender": "SmallUserInstance",
    "receiver": "SmallUserInstance",
    "send_at": "datetime"
  }
  ```
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`

## Demande d'amis
```
🔒 GET https://localhost:4443/api/users/me/friend_requests/<int:friends_request_id>/
```
- **Description** : Récupère une instance de demande d'amis.
- **Réponse (succès)** :
  - results:
  ```json
  {
    "id": "int",
    "sender": "SmallUserInstance",
    "receiver": "SmallUserInstance",
    "send_at": "datetime"
  }
  ```
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`
  - `404 Not Found` : Si l'utilisateur n'existe pas ou que l'utilisateur qui tente d'accéder à l'instance de demande d'amis, n'est ni celui qui l'a envoyé, ni celui qui l'a reçu.

```
🔒 DELETE https://localhost:4443/api/users/me/friend_requests/<int:friends_request_id>/
```
- **Description** :  Supprime l’instance de demande d'amis.
- **Codes de réponse** :
  - `204 No Content`
  - `401 Unauthorized`
  - `404 Not Found` : Si l'utilisateur n'existe pas ou que l'utilisateur qui tente d'accéder à l'instance de demande d'amis, n'est ni celui qui l'a envoyé, ni celui qui l'a reçu.

```
🔒 POST https://localhost:4443/api/users/me/friend_requests/<int:friends_request_id>/
```
- **Description** : Accepte une demande d'amis.
- **Réponse (succès)** :
  - results:
  ```json
  {
    "id": "int",
    "friend": "SmallUserInstance",
    "friend_win": "int",
    "me_win": "int",
    "friends_since": "datetime",
    "matches_play_against": "int",
    "matches_played_together": "int",
    "matches_won_together": "int"
  }
  ```
- **Codes de réponse** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l’utilisateur qui a envoyé la demande tente d’accepter lui-même la demande
  - `404 Not Found` : Si l'utilisateur n'existe pas ou que l'utilisateur qui tente d'accéder à l'instance de demande d'amis, n'est ni celui qui l'a envoyé, ni celui qui l'a reçu.

## Amis
```
🔒 GET https://localhost:4443/api/users/me/friends/
```
- **Description** : Récupère la liste de toutes les amitiés de l'utilisateur.
- **Réponse (succès)** :
  - results:
  ```json
  {
    "id": "int",
    "friend": "SmallUserInstance",
    "friend_win": "int",
    "me_win": "int",
    "friends_since": "datetime",
    "matches_play_against": "int",
    "matches_played_together": "int",
    "matches_won_together": "int"
  }
  ```
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`

```
🔒 DELETE https://localhost:4443/api/users/me/friends/<int:friends_id>/
```
- **Description** : Supprime une amitié.
- **Codes de réponse** :
  - `204 No Content`
  - `401 Unauthorized`
  - `404 Not Found` : Si l’amitié n’existe pas ou que celui qui fait la requête ne fait pas partie de l’amitié

## Bloquer
```
🔒 GET https://localhost:4443/api/users/me/blocked/
```
- **Description** : Récupère la liste de tous les utilisateurs bloqués.
- **Réponse (succès)** :
  - results:
  ```json
  {
    "id": "int",
    "blocked": "SmallUserInstance",
    "blocked_at": "datetime"
  }
  ```
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`

```
🔒 POST https://localhost:4443/api/users/me/blocked/
```
- **Description** : Bloque un utilisateur.
- **Body (JSON)** :
  ```json
  {
    "*user_id": "int"
  }
  ```
- **Réponse (succès)** :
  - results:
  ```json
  {
    "id": "int",
    "blocked": "SmallUserInstance",
    "blocked_at": "datetime"
  }
  ```
- **Codes de réponse** :
  - `201 Ressource Created`
  - `401 Unauthorized`
  - `403 Permission Denied` : Si l’utilisateur tente de se bloquer soi-même ou que l'utilisateur a déjà bloqué 50 utilisateurs.
  - `404 Not Found` : Si l'utilisateur n'existe pas ou que l'utilisateur est un utilisateur invité ou que l'utilisateur a déjà bloqué l'utilisateur qui fait la requête.
  - `409 Conflict` : Si l'utilisateur a déjà bloqué user_id.

```
🔒 DELETE https://localhost:4443/api/users/me/blocked/<int:blocked_id>/
```
- **Description** : Supprime l'instance de bloc (débloque l'utilisateur).
- **Codes de réponse** :
  - `204 No Content`
  - `401 Unauthorized`
  - `404 Not Found` : Si blocked_id n'existe pas ou que l'utilisateur qui fait la requête n'est pas le même qui a bloqué l'utilisateur dans blocked_id.

## Données de l'utilisateur
```
🔒 GET https://localhost:4443/api/users/me/download-data/
```
- **Description** : Récupère un fichier .json avec toutes les données de l'utilisateur.
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
  - Dans `ChatInstance` le champ `last_message` est remplacé par le champ `messages` qui est une liste de tous les messages de la conversation.
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`

## Photo de profil
```
🔒 GET https://localhost:4443/api/users/profile-pictures/
```
- **Description** : Récupère la liste de toutes les photos de profil disponible.
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
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`

```
🔒 PUT https://localhost:4443/api/users/profile-picture/<int:id>/
```
- **Description** : Mets à jour la photo de profil de l'utilisateur.
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
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`
  - `403 Permission Denied` : L'utilisateur n'a pas débloqué la photo de profil.
  - `404 Not Found` : La photo de profile demande n'existe pas.

## Statistiques
```
🔒 GET https://localhost:4443/api/users/me/stats/
```
- **Description** : Récupère la liste des statistiques sur tous les modes de jeux. Il n'y a pas de statistique pour le mode de jeu `custom_game`. Il y a des statistiques avec pour mode de jeu `global`. Cela correspond aux statistiques du joueur sur tous les modes de jeu. L'instance `global` se trouve toujours à l'index 0. Même si les données retournées sont sous forme de liste, cet endpoint n'a pas de système de pagination, le nombre de résultats étant fixe.
- **Réponse (succès)** :
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
  - Le champ `own_goals` est renvoyé uniquement si le mode de jeu est `clash`.
  - Le champ `tournament_wins` est renvoyé uniquement si le mode de jeu est `tournament`.
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`

## Statistiques du mode de jeu ranked
```
🔒 GET https://localhost:4443/api/users/me/stats/ranked/
```
- **Description** : Récupère la liste de l'evolution du nombre de trophées au cours des matchs.
- **Réponse (succès)** :
  - results:
  ```json
  {
    "id": "int",
    "trophies": "int",
    "total_trophies": "int",
    "at": "datetime"
  }
  ```
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`


# SSE

```
🔒 GET https://localhost:4443/sse/users/
```
- **Description** :  Permet de se connecter au SSE.
- **Réponse (succès)** :
  - results:
```
event: event_name\n
data: {data}\n\n
```
- **Codes de réponse** :
  - `200 OK`
  - `401 Unauthorized`

# Event SSE
```
🔒 GET https://localhost:4443/api/private/users/
```
- **Description** : Permet de créer un event SSE.
- **Body (JSON)** :
  ```json
  {
    "*users_id": "list[int]",
    "*event_code": "str",
    "data": "dict | None",
    "kwargs": "dict | None"
  }
  ```
  - **Réponse (succès)** :
  {
    "*users_id": "list[int]",
    "*event_code": "str",
    "data": "dict | None",
    "kwargs": "dict | None"
  }
- **Codes de réponse** :
  - `201 Ressource Created`
  - `400 Bad Request`
  - `404 Not Found` : Si aucun des utilisateurs envoyé existe ou qu'aucun des utilisateurs envoyé n'est connecté.

## Message
- ***receive-message*** est envoyé lorsque que l’utilisateur reçoit un message. data: *MessageInstance*, kwargs : *username, message, chat_id*

## User
- ***delete-user*** est envoyé lorsque que l’utilisateur supprime son compte.

## Game
Event envoyé quand le joueur joue dans une game :
- ***game-start*** est envoyé à tous les utilisateurs de la game. data: *MatchInstance*

## Friend
Events envoyés pour la gestion des amitiés :
- ***accept-friend-request*** est envoyé à l'utilisateur faisant la demande d'amis, si jamais il est connecté. Il est envoyé si l'utilisateur recevant la demande accepte la demande. data: *FriendInstance*, kwargs : *username*
- ***receive-friend-request*** est envoyé à l'utilisateur recevant la demande d'amis, si jamais il est connecté. Il est envoyé si l'utilisateur reçoit une demande d'amis. data: *FriendRequestInstance*, kwargs : *id, username*
- ***reject-friend-request*** est envoyé à l'utilisateur faisant la demande d'amis, si jamais il est connecté. Il est envoyé si jamais l'utilisateur recevant la demande rejette la demande, si l'utilisateur recevant la demande bloque celui l'envoyant, ou si l'utilisateur recevant la demande supprime son compte. data: *{"id" : FriendRequestInstance.id}*
- ***cancel-friend-request*** est envoyé à l'utilisateur recevant la demande d'amis, si jamais il est connecté. Il est envoyé si jamais l'utilisateur envoyant la demande d'amis annule l'envoie de cette demande d'amis, si l'utilisateur envoyant la demande d'amis bloque celui qui la reçoit *(uniquement dans ce cas, l'event est envoyé aux deux utilisateurs)*, ou si l'utilisateur envoyant la demande d'amis supprime son compte. data: *{"id" : FriendRequestInstance.id}*
- ***delete-friend*** est envoyé à l'autre utilisateur de la relation d'amitié, si jamais il est connecté. Il est envoyé si jamais un des utilisateurs supprime l'amitié, si l'un des deux utilisateurs bloque l'autre, ou si l'un des deux utilisateurs supprime son compte. data: *{"id" : FriendInstance.id}*

## Lobby
Events envoyés quand l'utilisateur est dans un lobby :
- ***lobby-join*** est envoyé à tous les utilisateurs déjà présents dans le lobby afin de les informer qu'un nouvel utilisateur a rejoint le lobby. data: *LobbyParticipantInstance*, kwargs : *username*
- ***lobby-leave*** est envoyé à tous les utilisateurs présents dans le lobby afin de les informer qu'un utilisateur à quitter le lobby. data: *{"id" : "int"}*, kwargs : *username*
- ***lobby-banned*** est envoyé à l'utilisateur banni. Les autres participants du lobby reçoivent un event *lobby-leave*.
- ***lobby-message*** est envoyé à tous les utilisateurs présents dans le lobby (excepté l'auteur du message). kwargs : *username*
- ***lobby-update*** est envoyé à tous les utilisateurs présents dans le lobby (excepté le créateur) afin de les informer que les paramètres du lobby ont été changés. data: *LobbyInstance* (uniquement les champs qui ont été modifiés).
- ***lobby-update-participant*** est envoyé à tous les utilisateurs présents dans le lobby (excepté celui qui performe la modification) afin de les informer que les paramètres de l'utilisateur ont été changés. data: *LobbyParticipantInstance* (uniquement les champs qui ont été modifiés à savoir où `creator`, `team` ou `is_ready`).
- ***lobby-spectate-game*** est envoyé à tous les utilisateurs présents dans la team "spectator" lorsqu'une game commence. data : *{"code" : "str"}*
- ***lobby-destroy*** est envoyé à tous les utilisateurs utilisateur invité présents dans le lobby dans le cas où le creator quitte le lobby, et que plus aucun utilisateur enregistré reste dans le lobby, afin de les informer le lobby a été détruit.

## Tournament
Events envoyés quand l'utilisateur est dans un tournoi :
- ***tournament-join*** est envoyé à tous les utilisateurs déjà présents dans le tournoi afin de les informer qu'un nouvel utilisateur a rejoint le tournoi. data: *TournamentParticipantInstance*, kwargs : *username*
- ***tournament-leave*** est envoyé à tous les utilisateurs présents dans le tournoi afin de les informer qu'un utilisateur à quitter le tournoi. data: *{"id" : "int"}*, kwargs : *username*
- ***tournament-banned*** est envoyé à l'utilisateur banni. Les autres participants du tournoi reçoivent un event *tournament-leave*.
- ***tournament-message*** est envoyé à tous les utilisateurs présents dans le tournoi (excepté l'auteur du message). kwargs : *username*
- ***tournament-start-at*** est envoyé à tous les participants du tournoi pour les informer que le tournoi commence à "start_at". C'est lorsque le tournoi est rempli à 80% de la taille. Il y a alors une période de 20 secondes d'attente avant que le tournoi commence. Si une personne quitte pendant ce temps d'attente, l'event *tournament-start-cancel* est envoyé à tous les utilisateurs encore présents et "start_at" est remis à None. data: *{"id" : "int", "start_at" : "datetime"}*
- ***tournament-start-cancel*** est envoyé à tous les participants du tournoi pour les informer que le lancement du tournoi est annulé. data: *{"id" : "int", "start_at" : "datetime"}*
- ***tournament-start*** est envoyé à tous les participants du tournoi pour les informer que le tournoi commence (soit parce que le "start_at" est passé ou parce que le tournoi est complet). Il y a alors un timer de trois secondes avant que les game se lance, afin d'avoir le temps de voir le bracket (qui est envoyé dans les data). data: *TournamentInstance*
- ***tournament-available-spectate-matches*** est envoyé à tous les participants du tournoi éliminé pour qu'il puisse regarder les matchs restant en tant que spectateur. data: *{"game_id" : "game_code", ...}*
- ***tournament-match-finish*** est envoyé à tous les participants du tournoi pour les informer du résultat d'un match. data: *TournamentInstance*, kwargs : *winner, looser, score_winner, score_looser, finish_reason*
- ***tournament-finish*** est envoyé à tous les participants du tournoi pour les informer que le tournoi est fini. kwargs : *id, name, username*

## Invite
Event envoyé quand un joueur invite un autre joueur dans un lobby ou un tournoi :
- ***invite-clash*** est envoyé à l'utilisateur pour rejoindre un lobby clash. data : *{"id" : "int", "code" : "str"}*, kwargs : *username, code*
- ***invite-1v1*** est envoyé à l'utilisateur pour rejoindre une game_custom en 1v1. data : *{"id" : "int", "code" : "str"}*, kwargs : *username, code*
- ***invite-3v3*** est envoyé à l'utilisateur pour rejoindre une game_custom en 3v3. data : *{"id" : "int", "code" : "str"}*, kwargs : *username, code*
- ***invite-tournament*** est envoyé à l'utilisateur pour rejoindre un tournoi. data : *{"id" : "int", "code" : "str"}*, kwargs : *username, code*
En target est envoyé l'URL à mettre dans le navigateur dans le cas où l'utilisateur accepte l'invitation.

## User
- ***user-delete*** est envoyé à l'utilisateur qui supprime ses données. Par exemple, si plusieurs clients sont connectés, un des clients supprime son compte, les autres clients sont au courant, et peuvent delog l'utilisateur.
- ***profile-picture-unlocked*** est envoyé à l'utilisateur qui débloque une photo de profil. data : *ProfilePictureInstance*, kwargs : *id*, taget : *use, see all*
