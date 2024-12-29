import json
from enum import Enum

import redis
from django.db.models import QuerySet
from lib_transcendence.exceptions import MessagesException, ServiceUnavailable
from lib_transcendence.sse_events import EventCode
from rest_framework.exceptions import ParseError

from users.models import Users


# todo reset to 0 notfication when sended
# todo handle notification for chat
# todo when retrieve many user, handle friend field
# todo when create match return user instance not only id
# todo when create match return teams id not list

def get_username(user_id):
    if isinstance(user_id, str):
        return user_id
    try:
        return Users.objects.get(id=user_id).username
    except Users.DoesNotExist:
        return 'DeleteUser'


class SSEType(Enum):
    NOTIFICATION = 'notification'
    EVENT = 'event'


class UrlType(Enum):
    URL = 'url'
    API = 'api'
    WS = 'websocket'


class Service(Enum):
    AUTH = 'auth'
    CHAT = 'chat'
    FRIENDS = 'friends'
    GAME = 'game'
    INVITE = 'invite'
    LOBBY = 'lobby'
    TOURNAMENT = 'tournament'


class Target:
    def __init__(self, url: str, method: str = None, display_name: str = None, display_icon: str = None, type: UrlType = None):
        self.url = url
        if type is not None:
            self.type = type
        elif method is None:
            self.type = UrlType.URL
        else:
            self.type = UrlType.API
        self.method = method
        self.display_name = display_name
        self.display_icon = display_icon

    def dumps(self, data):
        return {
            'url': self.url.format(**data),
            'type': self.type.name,
            'method': self.method,
            'display_name': self.display_name,
            'display_icon': self.display_icon,
        }


class Event:
    def __init__(self, service: Service, code: EventCode, fmessage=None, target: list[Target] | Target = None, type: SSEType = None):
        self.service = service
        self.code = code
        self.type = type
        self.fmessage = fmessage
        if isinstance(target, Target):
            target = [target]
        if type is not None:
            self.type = type
        elif target is None:
            self.type = SSEType.EVENT
        else:
            self.type = SSEType.NOTIFICATION
        self.target = target

    def dumps(self, data=None, kwargs=None):
        if self.fmessage is None:
            message = ''
        elif kwargs is not None:
            if 'username' in kwargs:
                kwargs['username'] = get_username(kwargs['username'])
            message = self.fmessage.format(**kwargs)
        else:
            message = self.fmessage

        result = {
            'service': self.service.value,
            'event_code': self.code.value,
            'type': self.type.value,
            'message': message,
            'target': None if self.target is None else [t.dumps(data) for t in self.target],
            'data': data,
        }
        return json.dumps(result)


delete_user = Event(Service.AUTH, EventCode.DELETE_USER)

send_message = Event(Service.CHAT, EventCode.SEND_MESSAGE, '{username}: {message}', Target('/chat/{id}/')) # todo format

accept_friend_request = Event(Service.FRIENDS, EventCode.ACCEPT_FRIEND_REQUEST, '{username} has accepted your friend request.', type=SSEType.NOTIFICATION)
receive_friend_request = Event(Service.FRIENDS, EventCode.RECEIVE_FRIEND_REQUEST, '{username} wants to be friends with you.', [Target('/api/users/me/friend_requests/{id}/', 'POST', display_icon='/icon/accept.png'), Target('/api/users/me/friend_requests/{id}/', 'DELETE', display_icon='/icon/decline.png')])
reject_friend_request = Event(Service.FRIENDS, EventCode.REJECT_FRIEND_REQUEST)
cancel_friend_request = Event(Service.FRIENDS, EventCode.CANCEL_FRIEND_REQUEST)
delete_friend = Event(Service.FRIENDS, EventCode.DELETE_FRIEND)

game_start = Event(Service.GAME, EventCode.GAME_START, 'You play in a game.', Target('/ws/game/{code}/', type=UrlType.WS)) # todo check how work # todo format

invite_1v1 = Event(Service.INVITE, EventCode.INVITE_1V1, '{username} has challenged you to a game.', Target('/api/play/lobby/{code}/', 'POST', display_name='join')) # todo format
invite_clash = Event(Service.INVITE, EventCode.INVITE_CLASH, '{username} inviting you to join a clash game.', Target('/api/play/lobby/{code}/', 'POST', display_name='join')) # todo format
invite_custom_game = Event(Service.INVITE, EventCode.INVITE_CUSTOM_GAME, '{username} inviting you to join a custom game.', Target('/api/play/lobby/{code}/', 'POST', display_name='join')) # todo format
invite_tournament = Event(Service.INVITE, EventCode.INVITE_TOURNAMENT, '{username} inviting you to join his tournament.', Target('/api/play/tournament/{code}/', 'POST', display_name='join')) # todo format

lobby_join = Event(Service.LOBBY, EventCode.LOBBY_JOIN, '{username} have joined the lobby.')
lobby_leave = Event(Service.LOBBY, EventCode.LOBBY_LEAVE, '{username} have left the lobby.')
lobby_update = Event(Service.LOBBY, EventCode.LOBBY_UPDATE)
lobby_update_participant = Event(Service.LOBBY, EventCode.LOBBY_UPDATE_PARTICIPANT)
lobby_ban = Event(Service.LOBBY, EventCode.LOBBY_BAN, 'You have been baned from the lobby.')
lobby_destroy = Event(Service.LOBBY, EventCode.LOBBY_DESTROY, 'The lobby has been destroyed.')

tournament_join = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_JOIN, '{username} have joined the tournament.') # todo format
tournament_leave = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_LEAVE, '{username} have left the tournament.') # todo format
tournament_start_3 = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_START_3, 'Tournament {name} start in 3 seconds.') # todo format
tournament_start_20 = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_START_20, 'Tournament {name} start in 20 seconds.') # todo format
tournament_start_cancel = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_START_CANCEL)
tournament_seeding = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_SEEDING) # todo send all game (who play against who)
tournament_match_end = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_MATCH_END, '{winner} win against {looser}.') # todo format
tournament_finish = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_FINISH, 'The tournament {name} is now over. Well done to {winner}} for his victory!') # todo format

# 'update-status': {'type': SSEType.event, 'db_field': None, 'message': None, 'target': 'update status user view', 'required-data': ['user_id', 'new status']}, # todo handle update status

redis_client = redis.StrictRedis(host='event-queue')


def publish_event(users: Users | QuerySet[Users] | list[Users], event_code: EventCode, data=None, kwargs=None):
    event = globals().get(event_code.value.replace('-', '_'))
    if event is None:
        raise ParseError({'event_code': [MessagesException.ValidationError.INVALID_EVENT_CODE]}) # todo handle error

    if isinstance(users, Users):
        users = [users]
    elif isinstance(users, QuerySet):
        users = list(users)

    for user in users:
        if user.is_online:
            channel = f'events:user_{user.id}'

            print('EVENT', event, data, flush=True)
            try:
                redis_client.publish(channel, event.code.value + ':' + event.dumps(data, kwargs))
            except redis.exceptions.ConnectionError:
                raise ServiceUnavailable('event-queue')
