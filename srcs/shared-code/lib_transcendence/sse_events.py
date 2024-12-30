from enum import Enum

from lib_transcendence.exceptions import MessagesException, ServiceUnavailable
from lib_transcendence.request import request_service
from lib_transcendence import endpoints
from rest_framework.exceptions import APIException, NotFound


# todo make ban tournament
#  - handle sse event
#   * send leave to other members
#   * send ban to members that ban
#  - save all ban users in a tournament
#  - delete when tournament is delete
#  - check if time a user wants to join
class EventCode(Enum):
    DELETE_USER = 'delete-user'
    SEND_MESSAGE = 'send-message'
    ACCEPT_FRIEND_REQUEST = 'accept-friend-request'
    RECEIVE_FRIEND_REQUEST = 'receive-friend-request'
    REJECT_FRIEND_REQUEST = 'reject-friend-request'
    CANCEL_FRIEND_REQUEST = 'cancel-friend-request'
    DELETE_FRIEND = 'delete-friend'
    GAME_START = 'game-start'
    INVITE_1V1 = 'invite-1v1'
    INVITE_3V3 = 'invite-3v3'
    INVITE_CLASH = 'invite-clash'
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


def create_sse_event(
        users: list[int] | int,
        event_code: EventCode,
        data: dict,
        kwargs: dict | None = None,
):
    sse_data = {
        'users_id': [users] if isinstance(users, int) else users,
        'event_code': event_code.value,
    }

    if data is not None:
        sse_data['data'] = data

    if kwargs is not None:
        sse_data['kwargs'] = kwargs

    try:
        return request_service('users', endpoints.Users.event, 'POST', sse_data)
    except NotFound as e:
        raise e
    except APIException:
        raise ServiceUnavailable(MessagesException.ServiceUnavailable.SSE)
