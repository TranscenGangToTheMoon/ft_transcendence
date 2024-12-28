from enum import Enum

# todo make ban tournament
#  - handle sse event
#   * send leave to other members
#   * send ban to members that ban
#  - save all ban users in a tournament
#  - delete when tournament is delete
#  - check if time a user wants to join
class EventCode(Enum):
    CONNECTION_SUCCESS = 'connection-success'
    CONNECTION_CLOSE = 'connection-close'
    SEND_MESSAGE = 'send-message'
    ACCEPT_FRIEND_REQUEST = 'accept-friend-request'
    RECEIVE_FRIEND_REQUEST = 'receive-friend-request'
    REJECT_FRIEND_REQUEST = 'reject-friend-request'
    CANCEL_FRIEND_REQUEST = 'cancel-friend-request'
    DELETE_FRIEND = 'delete-friend'
    GAME_START = 'game-start'
    INVITE_1V1 = 'invite-1v1'
    INVITE_CLASH = 'invite-clash'
    INVITE_CUSTOM_GAME = 'invite-custom-game'
    INVITE_TOURNAMENT = 'invite-tournament'
    LOBBY_JOIN = 'lobby-join'
    LOBBY_LEAVE = 'lobby-leave'
    LOBBY_UPDATE = 'lobby-update'
    LOBBY_UPDATE_PARTICIPANT = 'lobby-update-participant'
    LOBBY_DESTROY = 'lobby-destroy'
    LOBBY_BAN = 'lobby-ban'
    TOURNAMENT_JOIN = 'tournament-join'
    TOURNAMENT_LEAVE = 'tournament-leave'
    TOURNAMENT_BAN = 'tournament-ban'
    TOURNAMENT_START_3 = 'tournament-start-3'
    TOURNAMENT_START_20 = 'tournament-start-20'
    TOURNAMENT_START_CANCEL = 'tournament-start-cancel'
    TOURNAMENT_SEEDING = 'tournament-seeding'
    TOURNAMENT_MATCH_END = 'tournament-match-end'
    TOURNAMENT_FINISH = 'tournament-finish'
