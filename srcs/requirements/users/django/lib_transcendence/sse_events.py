from lib_transcendence.exceptions import MessagesException, ServiceUnavailable
from lib_transcendence.request import request_service
from lib_transcendence import endpoints
from rest_framework.exceptions import APIException, NotFound

from lib_transcendence.validate_type import surchage_list


class EventCode:
    DELETE_USER = 'delete-user'
    RECEIVE_MESSAGE = 'receive-message'
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
    LOBBY_BANNED = 'lobby-banned'
    LOBBY_MESSAGE = 'lobby-message'
    LOBBY_UPDATE = 'lobby-update'
    LOBBY_UPDATE_PARTICIPANT = 'lobby-update-participant'
    LOBBY_DESTROY = 'lobby-destroy'
    TOURNAMENT_JOIN = 'tournament-join'
    TOURNAMENT_LEAVE = 'tournament-leave'
    TOURNAMENT_BANNED = 'tournament-banned'
    TOURNAMENT_MESSAGE = 'tournament-message'
    TOURNAMENT_START = 'tournament-start'
    TOURNAMENT_START_AT = 'tournament-start-at'
    TOURNAMENT_START_CANCEL = 'tournament-start-cancel'
    TOURNAMENT_MATCH_FINISH = 'tournament-match-finish'
    TOURNAMENT_FINISH = 'tournament-finish'
    PING = 'ping'

    @staticmethod
    def attr():
        return surchage_list(EventCode)


def create_sse_event(
        users: list[int] | int,
        event_code: EventCode,
        data: dict | None = None,
        kwargs: dict | None = None,
        raise_exception: bool = False,
):
    sse_data = {
        'users_id': [users] if isinstance(users, int) else users,
        'event_code': event_code,
    }

    if data is not None:
        sse_data['data'] = data

    if kwargs is not None:
        sse_data['kwargs'] = kwargs

    try:
        return request_service('users', endpoints.Users.event, 'POST', sse_data)
    except NotFound as e:
        if raise_exception:
            raise e
    except APIException:
        if raise_exception:
            raise ServiceUnavailable(MessagesException.ServiceUnavailable.SSE)
