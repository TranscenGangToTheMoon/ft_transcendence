from enum import Enum


# todo when kick lobby, tournamnet
class EventCode(Enum):
    CONNECTION_SUCCESS = 'connection-success'
    SEND_MESSAGE = 'send-message'
    ACCEPT_FRIEND_REQUEST = 'accept-friend-request'
    RECEIVE_FRIEND_REQUEST = 'receive-friend-request'
    GAME_START = 'game-start'
    INVITE_1V1 = 'invite-1v1'
    INVITE_CLASH = 'invite-clash'
    INVITE_CUSTOM_GAME = 'invite-custom-game'
    INVITE_TOURNAMENT = 'invite-tournament'
    LOBBY_JOIN = 'lobby-join'
    LOBBY_LEAVE = 'lobby-leave'
    LOBBY_UPDATE = 'lobby-update'
    TOURNAMENT_JOIN = 'tournament-join'
    TOURNAMENT_LEAVE = 'tournament-leave'
    TOURNAMENT_START_3 = 'tournament-start-3'
    TOURNAMENT_START_20 = 'tournament-start-20'
    TOURNAMENT_START_CANCEL = 'tournament-start-cancel'
    TOURNAMENT_SEEDING = 'tournament-seeding'
    TOURNAMENT_MATCH_END = 'tournament-match-end'
    TOURNAMENT_FINISH = 'tournament-finish'
