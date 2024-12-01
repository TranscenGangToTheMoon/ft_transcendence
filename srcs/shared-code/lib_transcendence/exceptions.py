from lib_transcendence.game import GameMode
from rest_framework import status
from rest_framework.exceptions import APIException


class MessagesException:
    class NotFound:
        USER_NOT_IN_GAME = 'This user is not in a game.'

        NOT_FOUND = '{obj} not found.'
        CREATOR = NOT_FOUND.format(obj='Creator')
        USER = NOT_FOUND.format(obj='User')
        FRIEND_REQUEST = NOT_FOUND.format(obj='Friend request')
        FRIENDSHIP = NOT_FOUND.format(obj='Friendship')

        NOT_BELONG = 'You do not belong to any {obj}.'
        NOT_BELONG_TOURNAMENT = NOT_BELONG.format(obj='tournament')

        NOT_PLAYING = 'You are not currently playing.'

    class ValidationError:
        REQUIRED = '{obj} is required.'
        USER_ID_REQUIRED = REQUIRED.format(obj='User id')
        REQUEST_REQUIRED = REQUIRED.format(obj='Request')
        REQUEST_DATA_REQUIRED = REQUIRED.format(obj='Request data')
        FIELD_REQUIRED = REQUIRED.format(obj='This field')

        _OBJS_REQUIRED = '{obj} are required.'
        TEAM_REQUIRED = _OBJS_REQUIRED.format(obj='Two teams')
        TOURNAMENT_ID_REQUIRED = REQUIRED.format(obj='Tournament id') + ' for tournament mode.'
        TOURNAMENT_STAGE_ID_REQUIRED = REQUIRED.format(obj='Stage tournament id') + ' for tournament mode.'

        USERNAME_NOT_ALLOWED = 'This username is not allowed.'
        USERNAME_LONGER_THAN_3_CHAR = 'Username must be at least 3 characters long.'
        USERNAME_SHORTER_THAN_30_CHAR = 'Username must be less than 30 characters long.'
        INVALIDE_CHAR = 'Use of an invlid character.'
        USERNAME_ALREAY_EXISTS = 'This username already exists.'

        ONLY_1V1_3V3_ALLOWED = 'Only 1v1 and 3v3 are allowed.'
        BO_MUST_BE = 'Best of must be 1, 3 or 5.'

        TEAMS_LIST = 'Teams must be a list.'
        TEAMS_NOT_EQUAL = 'Both teams must have the same number of players.'

        GAME_MODE_PLAYERS = '{obj} mode must have {n} players in each teams.'
        CLASH_3_PLAYERS = GAME_MODE_PLAYERS.format(obj='Clash', n=3)

        TOURNAMENT_MAX_SIZE = 'Tournament size must be less than or equal than 32.'
        TOURNAMENT_MIN_SIZE = 'Tournament size must be greater or equal than 4.'

    class NotAuthenticated:
        PASSWORD_CONFIRMATION_REQUIRED = 'Password confirmation is required to delete the account.'

    class AuthentificationFailed:
        INCORRECT_PASSWORD = 'Incorrect password.'

    class PermissionDenied:
        _GUEST_CANNOT_CREATE = 'Guest users cannot create {obj}.'
        GUEST_CANNOT_CREATE_LOBBY = _GUEST_CANNOT_CREATE.format(obj='lobby')
        GUEST_CANNOT_CREATE_TOURNAMENT = _GUEST_CANNOT_CREATE.format(obj='tournament')
        GUEST_USERS_NOT_ALLOWED = 'Guest users are not allowed to change their password.'
        GUEST_CANNOT_PLAY_RANKED = 'Guest users cannot play ranked games.'
        GUEST_UPDATE_USERNAME = 'Guest users can only update their username.'

        NOT_BELONG = 'You do not belong to this {obj}.'
        NOT_BELONG_TO_CHAT = NOT_BELONG.format(obj='chat')
        NOT_BELONG_LOBBY = NOT_BELONG.format(obj='lobby')
        NOT_BELONG_TOURNAMENT = NOT_BELONG.format(obj='tournament')
        NOT_BELONG_BLOCKED = 'This blocked user entry does not belong to you.'

        ONLY_CREATE_PRIVATE_MESSAGES = 'You can only create private messages.'

        CANNOT_CHAT_YOURSELF = 'You cannot chat with yourself.'
        KICK_YOURSELF = 'You cannot kick yourself.'
        BLOCK_YOURSELF = 'You cannot block yourself.'
        SEND_FRIEND_REQUEST_YOURSELF = 'You cannot send a friend request to yourself.'
        FRIEND_YOURSELF = 'You cannot be friends with yourself.'
        ACCEPT_FRIEND_REQUEST_YOURSELF = {'detail': 'you cannot accept your own friend request.'}

        CANNOT_UPDATE_GAME_MODE = 'You cannot update game mode.'

        IS_FULL = '{obj} is full.'
        TEAM_IS_FULL = IS_FULL.format(obj='Team')

        TOURNAMENT_ALREADY_STARTED = 'Tournament already started.'

        UPDATE_CLASH_MODE = f'You cannot update {GameMode.clash} lobby.'
        UPDATE_TEAM_CLASH_MODE = f'You cannot update team in {GameMode.clash} mode.'

        NOT_CREATOR = 'Only creator can update this {obj}.'

        CAN_CREATE_MORE_THAN_ONE_TOURNAMENT = 'You cannot create more than one tournament at the same time.'
        KICK_AFTER_START = 'You cannot kick user after the tournament start.'

        BLOCKED_USER = 'You blocked this user.'

        SEND_MORE_THAN_20_FRIEND_REQUESTS = 'You cannot send more than 20 friend requests at the same time.'
        BLOCK_MORE_THAN_50_USERS = 'You cannot block more than 50 users.'

        _NOT_ACCEPT = 'This user does not accept {obj}.'
        NOT_ACCEPT_CHAT = _NOT_ACCEPT.format(obj='new chat')
        NOT_ACCEPT_FRIEND_REQUEST = _NOT_ACCEPT.format(obj='friend requests')

    class Conflict:
        DEFAULT = 'Conflict.'
        _ALREADY = 'You are already in a {obj}.'
        ALREADY_IN_GAME = _ALREADY.format(obj='game')
        ALREADY_IN_TOURNAMENT = _ALREADY.format(obj='tournament')

    class ResourceExists:
        DEFAULT = 'Resource already exists.'
        CHAT = 'You are already chat with this user.'
        TEAM = 'You are already in this team.'
        BLOCK = 'You are already blocked this user.'
        FRIEND = 'You are already friends with this user.'
        FRIEND_REQUEST_SENT = 'You have already sent a friend request to this user.'
        FRIEND_REQUEST_RECEIVED = 'You have already received a friend request from this user.'

        JOIN = 'You already joined this {obj}.'

    class ServiceUnavailable:
        SERVICE_UNAVAILABLE = 'Failed to connect to {service} service.'

    class ValueError:
        RANGE_VALUE = 'Range lookup requires a tuple of two int.'


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = MessagesException.ServiceUnavailable.SERVICE_UNAVAILABLE
    default_code = 'service_unavailable'

    def __init__(self, service):
        self.detail = ServiceUnavailable.default_detail.format(service=service)


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
