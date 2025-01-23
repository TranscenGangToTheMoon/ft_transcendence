from typing import Literal

from lib_transcendence.game import GameMode
from rest_framework import status
from rest_framework.exceptions import APIException


class MessagesException:
    class NotFound:
        NOT_FOUND = '{obj} not found.'
        CREATOR = NOT_FOUND.format(obj='Creator')
        USER = NOT_FOUND.format(obj='User')
        USERS = NOT_FOUND.format(obj='Users')
        FRIEND_REQUEST = NOT_FOUND.format(obj='Friend request')
        FRIENDSHIP = NOT_FOUND.format(obj='Friendship')
        TOURNAMENT = NOT_FOUND.format(obj='Tournament')
        BLOCKED_INSTANCE = NOT_FOUND.format(obj='Blocked instance')
        MATCH = NOT_FOUND.format(obj='Match')
        CHAT = NOT_FOUND.format(obj='Chat')

        NOT_BELONG = 'You do not belong to any {obj}.'
        NOT_BELONG_TOURNAMENT = NOT_BELONG.format(obj='tournament')
        NOT_BELONG_GAME = NOT_BELONG.format(obj='game')

        NOT_PLAYING = 'You are not currently playing.'
        NOT_BELONG_MATCH = 'This user does not belong to any match.'

    class ValidationError:
        REQUIRED = '{obj} is required.'
        USER_ID_REQUIRED = REQUIRED.format(obj='User id')
        REQUEST_REQUIRED = REQUIRED.format(obj='Request')
        REQUEST_DATA_REQUIRED = REQUIRED.format(obj='Request data')
        FIELD_REQUIRED = REQUIRED.format(obj='This field')

        _OBJS_REQUIRED = '{obj} are required.'
        TEAM_REQUIRED = _OBJS_REQUIRED.format(obj='Two teams')

        USERNAME_NOT_ALLOWED = 'This username is not allowed.'
        USERNAME_LONGER_THAN_3_CHAR = 'Username must be at least 3 characters long.'
        USERNAME_SHORTER_THAN_30_CHAR = 'Username must be less than 30 characters long.'
        INVALIDE_CHAR = 'Use of an invlid character.'
        USERNAME_ALREAY_EXISTS = 'This username already exists.'
        PASSWORD_SHORTER_THAN_50_CHAR = 'Password must be less than 50 characters long.'
        SAME_PASSWORD = 'Password is the same as the old one.'

        ONLY_1V1_3V3_ALLOWED = 'Only 1v1 and 3v3 teams are allowed.'

        TEAMS_LIST = 'Teams must be a list.'
        TEAMS_NOT_EQUAL = 'Both teams must have the same number of players.'
        IN_BOTH_TEAMS = 'User cannot be in both teams.'

        GAME_MODE_PLAYERS = '{obj} mode must have {n} players in each teams.'
        CLASH_3_PLAYERS = GAME_MODE_PLAYERS.format(obj='Clash', n=3)

        INVALID_SERVICE = 'Invalid service.'
        INVALID_EVENT_CODE = 'Invalid event code.'

        DATA = 'Data must be a dictionary.'
        TRUE_ONLY = 'This field must be True.'
        NOT_BELONG_MATCH = 'This user does not belong to this match.'

        MISSING_KWARGS = 'Missing required kwargs.'
        MISSING_DATA = 'Missing required data.'

    class Authentication:
        NOT_CONNECTED_SSE = {'detail': 'You need to be connected to SSE to access this resource.', 'code': 'sse_connection_required'}
        AUTHENTICATION_FAILED = {'detail': 'Incorrect authentication credentials.', 'code': 'authentication_failed'}
        NOT_AUTHENTICATED = {'detail': 'Authentication credentials were not provided.', 'code': 'not_authenticated'}
        USER_NOT_FOUND = {'detail': 'User not found.', 'code': 'user_not_found'}

        PASSWORD_CONFIRMATION_REQUIRED = 'Password confirmation is required.'
        INCORRECT_PASSWORD = 'Incorrect password.'

    class PermissionDenied:
        GUEST = 'Guest users cannot perform this action.'
        GUEST_UPDATE_USERNAME = 'Guest users can only update their username.'
        GUEST_REQUIRED = 'You must be a guest user.'
        ALREADY_AUTHENTICATED = 'You are already authenticated.'

        NOT_BELONG = 'You do not belong to this {obj}.'
        NOT_BELONG_TO_CHAT = NOT_BELONG.format(obj='chat')
        NOT_BELONG_LOBBY = NOT_BELONG.format(obj='lobby')
        NOT_BELONG_TOURNAMENT = NOT_BELONG.format(obj='tournament')
        NOT_BELONG_GAME = NOT_BELONG.format(obj='game')
        NOT_BELONG_BLOCKED = 'This blocked user entry does not belong to you.'
        USER_NOT_BELONG = 'This user does not belong to this {obj}.'

        ONLY_CREATE_PRIVATE_MESSAGES = 'You can only create private messages.'

        CANNOT_CHAT_YOURSELF = 'You cannot chat with yourself.'
        BAN_YOURSELF = 'You cannot ban yourself.'
        INVITE_YOURSELF = 'You cannot invite yourself.'
        BLOCK_YOURSELF = 'You cannot block yourself.'
        SEND_FRIEND_REQUEST_YOURSELF = 'You cannot send a friend request to yourself.'
        FRIEND_YOURSELF = 'You cannot be friends with yourself.'
        ACCEPT_FRIEND_REQUEST_YOURSELF = {'detail': 'you cannot accept your own friend request.'}

        CANNOT_UPDATE_GAME_MODE = 'You cannot update game mode.'

        IS_FULL = '{obj} is full.'
        TEAM_IS_FULL = IS_FULL.format(obj='Team')

        TOURNAMENT_ALREADY_STARTED = 'Tournament already started.'

        UPDATE_CLASH_MODE = f'You cannot update {GameMode.CLASH} lobby.'
        UPDATE_TEAM_CLASH_MODE = f'You cannot update team in {GameMode.CLASH} mode.'

        NOT_CREATOR = 'Only creator can update this {obj}.'

        CAN_CREATE_MORE_THAN_ONE_TOURNAMENT = 'You cannot create more than one tournament at the same time.'

        _AFTER_START = 'You cannot {obj} after the tournament start.'
        BAN_AFTER_START = _AFTER_START.format(obj='ban')
        INVITE_AFTER_START = _AFTER_START.format(obj='invite')

        BLOCKED_USER = 'You blocked this user.'

        SEND_MORE_THAN_20_FRIEND_REQUESTS = 'You cannot send more than 20 friend requests at the same time.'
        BLOCK_MORE_THAN_50_USERS = 'You cannot block more than 50 users.'

        _NOT_ACCEPT = 'This user does not accept {obj}.'
        NOT_ACCEPT_CHAT = _NOT_ACCEPT.format(obj='new chat')
        NOT_ACCEPT_FRIEND_REQUEST = _NOT_ACCEPT.format(obj='friend requests')

        INVITE_NOT_FRIEND = 'You can only invite friends.'

        MATCH_NOT_FINISHED = 'Match cannot be set as finished.'
        IN_GAME = 'You cannot perform this action when you playing.'
        LOBBY_IN_GAME = 'You cannot perform this action the lobby is playing.'

    class Conflict:
        DEFAULT = 'Conflict.'
        _ALREADY = 'You are already in a {obj}.'
        ALREADY_IN_GAME = _ALREADY.format(obj='game')
        ALREADY_IN_TOURNAMENT = _ALREADY.format(obj='tournament')
        USER_ALREADY_IN_GAME = 'Users are already in a game.'

    class ResourceExists:
        DEFAULT = 'Resource already exists.'
        CHAT = 'You are already chat with this user.'
        TEAM = 'You are already in this team.'
        BLOCK = 'You are already blocked this user.'
        FRIEND = 'You are already friends with this user.'
        FRIEND_REQUEST_SENT = 'You have already sent a friend request to this user.'
        FRIEND_REQUEST_RECEIVED = 'You have already received a friend request from this user.'
        SSE = 'You are already connected to SSE.'
        USER = 'This user is already in this {obj}.'
        MATCH = 'This match is already finished.'

        JOIN = 'You already joined this {obj}.'

    class InternalServerError:
        CODE_GENERATION = 'Code generation failed.'

    class ServiceUnavailable:
        SERVICE_UNAVAILABLE = 'Failed to connect to {service} service.'
        SSE = 'Failed to create SSE event.'
        game = SERVICE_UNAVAILABLE.format(service='game')

    class ThrottledError:
        DEFAULT = 'Request was throttled.'


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = MessagesException.ServiceUnavailable.SERVICE_UNAVAILABLE
    default_code = 'service_unavailable'

    def __init__(self, service: Literal['auth', 'chat', 'game', 'matchmaking', 'event-queue', 'users']):
        if service in ['auth', 'chat', 'game', 'matchmaking', 'event-queue', 'users']:
            self.detail = ServiceUnavailable.default_detail.format(service=service)
        else:
            self.detail = service


class ResourceExists(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = MessagesException.ResourceExists.DEFAULT
    default_code = 'resource_exists'

    def __init__(self, detail=None):
        if detail is None:
            detail = self.default_detail
        self.detail = detail


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = MessagesException.Conflict.DEFAULT
    default_code = 'conflict'

    def __init__(self, detail):
        if detail is None:
            detail = self.default_detail
        self.detail = detail


class Throttled(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = MessagesException.ThrottledError.DEFAULT
    default_code = 'throttled'
