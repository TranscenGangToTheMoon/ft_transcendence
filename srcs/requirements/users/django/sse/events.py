import json

import redis
from django.db.models import QuerySet
from rest_framework.exceptions import ParseError

from lib_transcendence import endpoints
from lib_transcendence.exceptions import MessagesException, ServiceUnavailable
from lib_transcendence.sse_events import EventCode
from lib_transcendence.utils import datetime_serializer
from users.models import Users


def get_username(user_id):
    if isinstance(user_id, str):
        return user_id
    try:
        return Users.objects.get(id=user_id).username
    except Users.DoesNotExist:
        return 'DeleteUser'


class SSEType:
    NOTIFICATION = 'notification'
    EVENT = 'event'


class UrlType:
    URL = 'url'
    API = 'api'
    WS = 'websocket'


class Service:
    AUTH = 'auth'
    CHAT = 'chat'
    FRIENDS = 'friends'
    GAME = 'game'
    INVITE = 'invite'
    LOBBY = 'lobby'
    TOURNAMENT = 'tournament'
    USER = 'user'


class Target:

    def __init__(self, url: str, method: str = None, display_name: str = None, display_icon: str = None, type: str = None):
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
            'type': self.type,
            'method': self.method,
            'display_name': self.display_name,
            'display_icon': None if self.display_icon is None else f'/assets/{self.display_icon}',
        }


class Event:

    def __init__(self, service, code: EventCode, fmessage=None, target: list[Target] | Target = None, type: str = None):
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
        if data is None:
            data = {}

        if self.fmessage is None:
            message = ''
        elif kwargs is not None:
            for name in ('username', 'winner', 'looser'):
                if name in kwargs:
                    kwargs[name] = get_username(kwargs[name])
            try:
                message = self.fmessage.format(**kwargs)
            except KeyError as e:
                raise ParseError({'kwargs': {e.args[0]: MessagesException.ValidationError.MISSING_KWARGS}})
        else:
            message = self.fmessage

        try:
            target = None if self.target is None else [t.dumps(data) for t in self.target]
        except KeyError as e:
            raise ParseError({'data': {e.args[0]: MessagesException.ValidationError.MISSING_DATA}})

        result = {
            'service': self.service,
            'event_code': self.code,
            'type': self.type,
            'message': message,
            'target': target,
            'data': data,
        }
        return json.dumps(result, default=datetime_serializer)


class Events:
    ping = Event(Service.AUTH, EventCode.PING)
    delete_user = Event(Service.USER, EventCode.DELETE_USER)
    profile_picture_unlocked = Event(Service.USER, EventCode.PROFILE_PICTURE_UNLOCKED, 'You have unlocked new profile pictures!', [Target(endpoints.Users.fprofile_picture, 'PUT', display_name='use'), Target('/profile/pictures', 'PUT', display_name='see all')])

    receive_message = Event(Service.CHAT, EventCode.RECEIVE_MESSAGE, '{username}: {message}')

    accept_friend_request = Event(Service.FRIENDS, EventCode.ACCEPT_FRIEND_REQUEST, '{username} has accepted your friend request.', type=SSEType.NOTIFICATION)
    receive_friend_request = Event(Service.FRIENDS, EventCode.RECEIVE_FRIEND_REQUEST, '{username} wants to be friends with you.', [Target(endpoints.Users.ffriend_request, 'POST', display_icon='/icon/accept.png'), Target(endpoints.Users.ffriend_request, 'DELETE', display_icon='/icon/decline.png')])
    reject_friend_request = Event(Service.FRIENDS, EventCode.REJECT_FRIEND_REQUEST)
    cancel_friend_request = Event(Service.FRIENDS, EventCode.CANCEL_FRIEND_REQUEST)
    delete_friend = Event(Service.FRIENDS, EventCode.DELETE_FRIEND)

    game_start = Event(Service.GAME, EventCode.GAME_START, 'You play in a game.', Target('/ws/game/', type=UrlType.WS), type=SSEType.EVENT)

    invite_1v1 = Event(Service.INVITE, EventCode.INVITE_1V1, '{username} has challenged you to a game.', Target('/lobby/{code}', display_name='join'))
    invite_3v3 = Event(Service.INVITE, EventCode.INVITE_3V3, '{username} inviting you to join an epic 3v3 friendly battle.', Target('/lobby/{code}', display_name='join'))
    invite_clash = Event(Service.INVITE, EventCode.INVITE_CLASH, '{username} inviting you to join a clash game.', Target('/lobby/{code}', display_name='join'))
    invite_tournament = Event(Service.INVITE, EventCode.INVITE_TOURNAMENT, '{username} inviting you to join his tournament.', Target('/tournament/{code}', display_name='join'))

    lobby_join = Event(Service.LOBBY, EventCode.LOBBY_JOIN, '{username} have joined the lobby.')
    lobby_leave = Event(Service.LOBBY, EventCode.LOBBY_LEAVE, '{username} have left the lobby.')
    lobby_banned = Event(Service.LOBBY, EventCode.LOBBY_BANNED, 'You have been banned from this lobby.')
    lobby_message = Event(Service.LOBBY, EventCode.LOBBY_MESSAGE, '{username}: {message}')
    lobby_update = Event(Service.LOBBY, EventCode.LOBBY_UPDATE)
    lobby_update_participant = Event(Service.LOBBY, EventCode.LOBBY_UPDATE_PARTICIPANT)
    lobby_spectate_game = Event(Service.LOBBY, EventCode.LOBBY_SPECTATE_GAME)
    lobby_destroy = Event(Service.LOBBY, EventCode.LOBBY_DESTROY, 'The lobby has been destroyed.')

    tournament_join = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_JOIN, '{username} have joined the tournament.')
    tournament_leave = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_LEAVE, '{username} have left the tournament.')
    tournament_banned = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_BANNED, 'You have been banned from this tournament.')
    tournament_message = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_MESSAGE, '{username}: {message}')
    tournament_start = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_START, 'Tournament {name} start in 3 seconds.')
    tournament_start_at = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_START_AT, 'Tournament {name} start in 20 seconds.')
    tournament_start_cancel = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_START_CANCEL)
    tournament_match_finish = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_MATCH_FINISH, '{winner} win against {looser} {score_winner}-{score_looser}{finish_reason}.')
    tournament_available_spectate_matches = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_AVAILABLE_SPECTATE_MATCHES)
    tournament_finish = Event(Service.TOURNAMENT, EventCode.TOURNAMENT_FINISH, 'The tournament {name} is now over. Well done to {username} for his victory!', Target('/history/tournament/{id}', display_name='view'))


redis_client = redis.StrictRedis(host='event-queue')


def publish_event(users: Users | QuerySet[Users] | list[Users] | list[int] | int, event_code: str, data=None, kwargs=None):
    try:
        event = getattr(Events, event_code.replace('-', '_'))
    except AttributeError:
        raise ParseError({'event_code': [MessagesException.ValidationError.INVALID_EVENT_CODE]})

    if isinstance(users, Users | int):
        users = [users]
    elif isinstance(users, QuerySet):
        users = list(users)

    for user in users:
        if isinstance(user, int) or user.is_online:
            if isinstance(user, int):
                user_id = user
            else:
                user_id = user.id
            channel = f'events:user_{user_id}'

            try:
                redis_client.publish(channel, event.code + ':' + event.dumps(data, kwargs))
            except KeyError as e:
                raise ParseError({'kwargs': {e.args[0]: MessagesException.ValidationError.MISSING_KWARGS}})
            except redis.exceptions.ConnectionError:
                raise ServiceUnavailable('event-queue')
