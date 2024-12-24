from abc import ABC
from enum import Enum


class SSEType(Enum):
    NOTIFICATION = 'notification'
    EVENT = 'event'


class UrlType(Enum):
    URL = 'url'
    API = 'api'
    WS = 'websocket'


class Services(Enum):
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
        # todo handle url format

    def get_dict(self, **kwargs):
        return {
            'url': self.url.format(**kwargs),
            'type': self.type.name,
            'method': self.method,
            'display_name': self.display_name,
            'display_icon': self.display_icon,
        }


class Event:
    def __init__(self, service: Services, name: str, fmessage=None, target: list[Target] | Target = None, type: SSEType = None):
        self.service = service
        self.name = name
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
        # self.data = data todo handle for each
        # todo handle url format

    def get_dict(self, data=None, **kwargs):
        result = {
            'service': self.service,
            'event_code': self.name,
            'type': self.type.name,
            'message': self.fmessage.format(**kwargs),
            'target': [t.get_dict() for t in self.target],
        }
        if data is not None:
            result['data'] = data
        return result


connection_success = Event(Services.AUTH, 'connection-success', 'Connection has been successfully established.'),

send_message = Event(Services.CHAT, 'send_message', '{username}: {message}', Target('/chat/{id}/'))

accept_friend_request = Event(Services.FRIENDS, 'accept-friend-request', '{username} has accepted your friend request.', type=SSEType.NOTIFICATION),
receive_friend_request = Event(Services.FRIENDS, 'receive-friend-request', '{username} wants to be friends with you.', [Target('/api/users/me/friend_requests/{id}/', 'POST', display_icon='/icon/accept.png'), Target('/api/users/me/friend_requests/{id}/', 'DELETE', display_icon='/icon/decline.png')]),

game_start = Event(Services.GAME, 'start', 'You play in a game.', Target('/ws/game/{code}/', type=UrlType.WS)), # todo check how work

challenge = Event(Services.INVITE, 'challenge', '{username} has challenged you to a game.', Target('/api/play/lobby/{code}/', 'POST', display_name='join')),
invite_clash = Event(Services.INVITE, 'clash', '{username} inviting you to join a clash game.', Target('/api/play/lobby/{code}/', 'POST', display_name='join')),
invite_custom_game = Event(Services.INVITE, 'custom-game', '{username} inviting you to join a custom game.', Target('/api/play/lobby/{code}/', 'POST', display_name='join')),
invite_tournament = Event(Services.INVITE, 'tournament', '{username} inviting you to join his tournament.', Target('/api/play/tournament/{code}/', 'POST', display_name='join')),

lobby_join = Event(Services.LOBBY, 'join', '{username} have joined the lobby.'),
lobby_leave = Event(Services.LOBBY, 'leave', '{username} have left the lobby.'),
lobby_set_ready = Event(Services.LOBBY, 'set-ready', '{username} is now ready to play.'),

tournament_join = Event(Services.TOURNAMENT, 'join', '{username} have joined the tournament.'),
tournament_leave = Event(Services.TOURNAMENT, 'leave', '{username} have left the tournament.'),
tournament_start_3 = Event(Services.TOURNAMENT, 'start-3', 'Tournament {name} start in 3 seconds.'),
tournament_start_20 = Event(Services.TOURNAMENT, 'start-20', 'Tournament {name} start in 20 seconds.'),
tournament_start_cancel = Event(Services.TOURNAMENT, 'start-cancel'),
tournament_seeding = Event(Services.TOURNAMENT, 'seeding'), # todo send all game (who play against who)
tournament_match_end = Event(Services.TOURNAMENT, 'match-end', '{winner} win against {looser}.'),
tournament_finish = Event(Services.TOURNAMENT, 'finish', 'The tournament {name} is now over. Well done to {winner}} for his victory!'),

# 'update-status': {'type': SSEType.event, 'db_field': None, 'message': None, 'target': 'update status user view', 'required-data': ['user_id', 'new status']}, # todo handle update status
