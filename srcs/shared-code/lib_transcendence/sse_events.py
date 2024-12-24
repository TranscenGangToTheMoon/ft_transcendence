from enum import Enum


class EventsName(Enum):
    CONNECTION_SUCCESS = 'connection_success'
    SEND_MESSAGE = 'send_message'
    ACCEPT_FRIEND_REQUEST = 'accept_friend_request'
    RECEIVE_FRIEND_REQUEST = 'receive_friend_request'
    CHALLENGE = 'challenge'
    INVITE_CLASH = 'invite_clash'
    INVITE_CUSTOM_GAME = 'invite_custom_game'
    INVITE_TOURNAMENT = 'invite_tournament'
    LOBBY_JOIN = 'lobby_join'
    LOBBY_LEAVE = 'lobby_leave'
    LOBBY_SET_READY = 'lobby_set_ready'
    GAME_START = 'game_start'
    TOURNAMENT_JOIN = 'tournament_join'
    TOURNAMENT_LEAVE = 'tournament_leave'
    TOURNAMENT_START_3 = 'tournament_start_3'
    TOURNAMENT_START_20 = 'tournament_start_20'
    TOURNAMENT_START_CANCEL = 'tournament_start_cancel'
    TOURNAMENT_SEEDING = 'tournament_seeding'
    TOURNAMENT_MATCH_END = 'tournament_match_end'
    TOURNAMENT_FINISH = 'tournament_finish'


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
        # todo handl url format


class Event:
    def __init__(self, service, name: str, fmessage=None, target: list[Target] | Target = None, type: SSEType = None):
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

# 'update-status': {'type': SSEType.event, 'db_field': None, 'message': None, 'target': 'update status user view', 'required-data': ['user_id', 'new status']}, # todo handle update status

events = [
    Event('auth', 'connection-success', 'Connection has been successfully established.'),

    Event('chat', 'send-message', '{username}: {message}', Target('/chat/{id}/')),

    Event('friends', 'accept-friend-request', '{username} has accepted your friend request.', type=SSEType.NOTIFICATION),
    Event('friends', 'receive-friend-request', '{username} wants to be friends with you.', [Target('/api/users/me/friend_requests/{id}/', 'POST', display_icon='/icon/accept.png'), Target('/api/users/me/friend_requests/{id}/', 'DELETE', display_icon='/icon/decline.png')]),

    Event('invite', 'challenge', '{username} has challenged you to a game.', Target('/api/play/lobby/{code}/', 'POST', display_name='join')),
    Event('invite', 'invite-clash', '{username} inviting you to join a clash game.', Target('/api/play/lobby/{code}/', 'POST', display_name='join')),
    Event('invite', 'invite-custom-game', '{username} inviting you to join a custom game.', Target('/api/play/lobby/{code}/', 'POST', display_name='join')),
    Event('invite', 'invite-tournament', '{username} inviting you to join his tournament.', Target('/api/play/tournament/{code}/', 'POST', display_name='join')),

    Event('lobby', 'join', '{username} have joined the lobby.'),
    Event('lobby', 'leave', '{username} have left the lobby.'),
    Event('lobby', 'set-ready', '{username} is now ready to play.'),

    Event('game', 'start', 'You play in a game.', Target('/ws/game/{code}/', type=UrlType.WS)), # todo check

    Event('tournament', 'join', '{username} have joined the tournament.'),
    Event('tournament', 'leave', '{username} have left the tournament.'),
    Event('tournament', 'start-3', 'Tournament {name} start in 3 seconds.'),
    Event('tournament', 'start-20', 'Tournament {name} start in 20 seconds.'),
    Event('tournament', 'start-cancel'),
    Event('tournament', 'seeding'), # todo send all game (who play against who)
    Event('tournament', 'match-start', '{user1} play against {user2}.'), # todo already handle by game ?
    Event('tournament', 'match-end', '{winner} win against {looser}.'),
    Event('tournament', 'finish', 'The tournament {name} is now over. Well done to {winner}} for his victory!'),
]
