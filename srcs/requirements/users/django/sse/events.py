import json

import redis
from lib_transcendence.exceptions import ServiceUnavailable


# todo reset to 0 notfication when sended
# todo handle notification for chat
# todo when retrieve many user, handle friend field
# todo when create match return user instance not only id
# todo when create match return teams id not list

class SSEType:
    notification = 'notification'
    event = 'event'


events = {
    'auth':
        {
            'connection-success': {'type': SSEType.event, 'db_field': None, 'message': 'Successfully connected !', 'target': None, 'requiere-data': None},
            'connection-close': {'type': SSEType.event, 'db_field': None, 'message': 'Connection needed to be close', 'target': 'disconnect the client', 'requiere-data': None}, # todo handle disconnect (when user delete account)
        },
    'chat':
        {
            'send-message': {'type': SSEType.notification, 'db_field': 'chat_notifications', 'message': '{username}: {message}', 'target': 'open chat with user sending message', 'requiere-data': ['message_instance (user instance send, chat id, message']},
        },
    'friends':
        {
            'accept-friend-requests': {'type': SSEType.notification, 'db_field': None, 'message': '{username} has accepted your friend request!', 'target': 'open friend profile (not usefull)', 'required-data': ['friend instance (friencd accpeting, friend receive, profile user instance accepting']},
            'receive-friend-requests': {'type': SSEType.notification, 'db_field': 'friend_notifications', 'message': '{username} want to become friend with you, accept ? warning peolple can be weird', 'target': 'v (for accepting) x (for rejecting) o (for blocking)', 'required-data': ['friend request instance (friend sending, friend receive, profile user instance sending']},
            'update-status': {'type': SSEType.event, 'db_field': None, 'message': None, 'target': 'update status user view', 'required-data': ['user_id', 'new status']}, # todo handle update status
        },
    'invite':
        {
            'invite-game': {'type': SSEType.notification, 'db_field': 'friend_notifications', 'message': '{username} challeging you to an epic battle, do you accept the challenge?', 'target': 'v (for accpeting challenge) x (for decline invitation)', 'required-data': ['user inviting instance', 'lobby code']},
            'invite-clash': {'type': SSEType.notification, 'db_field': None, 'message': '{username} inviting you to play clash, a 3v3 fun game !', 'target': 'v (for joinning clash) x (for decline invitation)', 'required-data': ['user inviting instance', 'lobby code']},
            'invite-custom-game': {'type': SSEType.notification, 'db_field': None, 'message': '{username} inviting you to play custom game !', 'target': 'v (for joinning custum game) x (for decline invitation)', 'required-data': ['user inviting instance', 'lobby code']},
            'invite-tournament': {'type': SSEType.notification, 'db_field': None, 'message': '{username} inviting you to play tournament {tournament.name} !', 'target': 'v (for joinning tournament) x (for decline invitation)', 'required-data': ['user inviting instance', 'lobby code']},
        },
    'lobby':
        {
            'join-lobby': {'type': SSEType.event, 'db_field': None, 'message': '{username} join the lobby', 'target': 'add user view', 'required-data': ['user instance joinning lobby']},
            'leave-lobby': {'type': SSEType.event, 'db_field': None, 'message': '{username} leave the lobby', 'target': 'remove user view', 'required-data': ['user instance leaving lobby']},
            'set-ready-lobby': {'type': SSEType.event, 'db_field': None, 'message': '{username} is ready to fight (useless ?)', 'target': 'update view and if all user are ready change view (replace it by searching view)', 'required-data': ['user instance set ready lobby']},
        },
    'game':
        { # todo when send game message, update profile
            'game-start': {'type': SSEType.event, 'db_field': None, 'message': '', 'target': 'connect to web socket and move players to game', 'required-data': ['game instance (teams, users id, profile, etcc)']},
        },
    'tournament': # todo make
        {
            'tournament-start-3': {'type': SSEType.event, 'db_field': None, 'message': '', 'target': None, 'required-data': []},
            'tournament-start-27': {'type': SSEType.event, 'db_field': None, 'message': '', 'target': None, 'required-data': []},
            'tournament-start-cancel': {'type': SSEType.event, 'db_field': None, 'message': '', 'target': None, 'required-data': []},
            'tournament-match-end': {'type': SSEType.event, 'db_field': None, 'message': '', 'target': None, 'required-data': []},
        },
}


redis_client = redis.StrictRedis(host='event-queue')


def publish_event(user_id, service, event_code, data=None):
    channel = f'events:user_{user_id}'
    event = events[service][event_code]

    try:
        message = {
            'service': service,
            'event_code': event_code,
            'type': event['type'],
            'message': event['message'],
            'target': event['target'],
        }
        if data is not None:
            message['data'] = data
        redis_client.publish(channel, json.dumps(message))
    except redis.exceptions.ConnectionError:
        raise ServiceUnavailable('event-queue')
