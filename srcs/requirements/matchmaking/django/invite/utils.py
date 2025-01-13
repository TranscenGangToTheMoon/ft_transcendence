from lib_transcendence import endpoints
from lib_transcendence.exceptions import MessagesException, ResourceExists, ServiceUnavailable
from lib_transcendence.services import request_users
from rest_framework.exceptions import PermissionDenied, APIException, NotFound

from lobby.models import LobbyParticipants
from tournament.models import TournamentParticipants


def invite_yourself(user_id, invite_user_id):
    if user_id == invite_user_id:
        raise PermissionDenied(MessagesException.PermissionDenied.INVITE_YOURSELF)


def validate_participants_for_inviting(model, me_id, invite_user_id):
    try:
        model.participants.get(user_id=invite_user_id)
        raise ResourceExists(MessagesException.ResourceExists.USER.format(obj=type(model).__name__.lower()))
    except (LobbyParticipants.DoesNotExist, TournamentParticipants.DoesNotExist):
        pass
    try:
        request_users(endpoints.Users.fare_friends.format(user1_id=me_id, user2_id=invite_user_id), 'GET')
    except NotFound:
        raise PermissionDenied(MessagesException.PermissionDenied.INVITE_NOT_FRIEND)
    except APIException:
        raise ServiceUnavailable('users')
