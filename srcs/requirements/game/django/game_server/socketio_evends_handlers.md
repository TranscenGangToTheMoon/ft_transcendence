# Game Server Socket.IO Handlers Documentation

This document provides an overview of the Socket.IO handlers used in your server implementation. The table below outlines the server-to-client and client-to-server interactions for each handler, along with descriptions and parameters.

| **Handler**      | **Server**                                                                                          | **Client**                                          |
|-------------------|----------------------------------------------------------------------------------------------------|---------------------------------------------------|
| `connect`        | **Description:** Verifies authentication, assigns the client to a room, and handles debug mode.      | **Description:** Sends authentication data.       |
|                   | **Parameters:** `sid`, `environ`, `auth`                                                           | **Parameters:** `auth` (e.g., `token`, `id`).     |
| `move_up`        | **Description:** Emits a `move_up` event to other clients in the room.                              | **Description:** Requests upward movement.        |
|                   | **Parameters:** `sid`.                                                                             | **Parameters:** None.                             |
| `move_down`      | **Description:** Emits a `move_down` event to other clients in the room.                            | **Description:** Requests downward movement.      |
|                   | **Parameters:** `sid`.                                                                             | **Parameters:** None.                             |
| `stop_moving`    | **Description:** Emits a `stop_moving` event with the updated racket position.                      | **Description:** Sends stop movement data.        |
|                   | **Parameters:** `sid`, `data` (contains `position`).                                               | **Parameters:** `position`.                       |
| `send_games`     | **Description:** Sends a list of active game codes.                                                 | **Description:** Requests a list of active games. |
|                   | **Parameters:** `sid`.                                                                             | **Parameters:** None.                             |
| `goal`           | **Description:** Updates the score and emits a `goal` event to the room.                            | **Description:** Notifies server of a goal event. |
|                   | **Parameters:** `sid`.                                                                             | **Parameters:** None.                             |
| `disconnect`     | **Description:** Removes the client from their assigned room and cleans up resources.               | **Description:** Disconnects from the server.     |
|                   | **Parameters:** `sid`.                                                                             | **Parameters:** None.                             |
| `move_up`        | **Description:** Notifies server that the player requests upward movement.                          | **Description:** Emits a `move_up` event. |
|                   | **Parameters:** None.                                                                              | **Parameters:** `sid`.                            |
| `move_down`      | **Description:** Notifies server that the player requests downward movement.                        | **Description:** Emits a `move_down` event. |
|                   | **Parameters:** None.                                                                              | **Parameters:** `sid`.                            |
| `stop_moving`    | **Description:** Notifies server to stop racket movement.                                           | **Description:** Emits a `stop_moving` event with racket position. |
|                   | **Parameters:** `position`.                                                                        | **Parameters:** `sid`, `data` (contains `position`). |
| `goal`           | **Description:** Notifies server of a goal event.                                                   | **Description:** Emits a `goal` event to the server. |
|                   | **Parameters:** None.                                                                              | **Parameters:** `sid`.                            |

**Note:**
- Client always emits events to the server, and the server emits events to clients. This is the standard flow of communication between the client and server.
- All moving events sent from the server (e.g., `move_up`, `move_down`, `stop_moving`) will skip the sender in the room (`skip_sid=sid`).

## Notes
- **Authentication:** Ensure proper authentication logic is implemented before production.
- **Error Handling:** Add comprehensive error handling to prevent server crashes due to unexpected inputs or states.
- **Debugging:** Remove or disable debug-specific code (`debug` token) before deploying to production.
