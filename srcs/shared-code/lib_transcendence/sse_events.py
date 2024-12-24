from abc import ABC
from enum import Enum


class SSEType(Enum):
    NOTIFICATION = 'notification'
    EVENT = 'event'


class UrlType(Enum):
    URL = 'url'
    API = 'api'
    WS = 'websocket'


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


class Event:
    def __init__(self, service: str, name: str, fmessage=None, target: list[Target] | Target = None, type: SSEType = None):
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


class Auth:
    connection_success = Event('auth', 'connection-success', 'Connection has been successfully established.'),


class Chat:
    send_message = Event('chat', 'send_message', '{username}: {message}', Target('/chat/{id}/'))


class Friends:
    accept_friend_request = Event('friends', 'accept-friend-request', '{username} has accepted your friend request.', type=SSEType.NOTIFICATION),
    receive_friend_request = Event('friends', 'receive-friend-request', '{username} wants to be friends with you.', [Target('/api/users/me/friend_requests/{id}/', 'POST', display_icon='/icon/accept.png'), Target('/api/users/me/friend_requests/{id}/', 'DELETE', display_icon='/icon/decline.png')]),


class Invite:
    challenge = Event('invite', 'challenge', '{username} has challenged you to a game.', Target('/api/play/lobby/{code}/', 'POST', display_name='join')),
    invite_clash = Event('invite', 'clash', '{username} inviting you to join a clash game.', Target('/api/play/lobby/{code}/', 'POST', display_name='join')),
    invite_custom_game = Event('invite', 'custom-game', '{username} inviting you to join a custom game.', Target('/api/play/lobby/{code}/', 'POST', display_name='join')),
    invite_tournament = Event('invite', 'tournament', '{username} inviting you to join his tournament.', Target('/api/play/tournament/{code}/', 'POST', display_name='join')),


class Lobby:
    join = Event('lobby', 'join', '{username} have joined the lobby.'),
    leave = Event('lobby', 'leave', '{username} have left the lobby.'),
    set_ready = Event('lobby', 'set-ready', '{username} is now ready to play.'),


class Game:
    start = Event('game', 'start', 'You play in a game.', Target('/ws/game/{code}/', type=UrlType.WS)), # todo check how work


class Tournament:
    join = Event('tournament', 'join', '{username} have joined the tournament.'),
    leave = Event('tournament', 'leave', '{username} have left the tournament.'),
    start_3 = Event('tournament', 'start-3', 'Tournament {name} start in 3 seconds.'),
    start_20 = Event('tournament', 'start-20', 'Tournament {name} start in 20 seconds.'),
    start_cancel = Event('tournament', 'start-cancel'),
    seeding = Event('tournament', 'seeding'), # todo send all game (who play against who)
    match_end = Event('tournament', 'match-end', '{winner} win against {looser}.'),
    finish = Event('tournament', 'finish', 'The tournament {name} is now over. Well done to {winner}} for his victory!'),

# 'update-status': {'type': SSEType.event, 'db_field': None, 'message': None, 'target': 'update status user view', 'required-data': ['user_id', 'new status']}, # todo handle update status
