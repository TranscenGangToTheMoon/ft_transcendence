from lib_transcendence.sse_events import EventCode, create_sse_event
from lib_transcendence.users import retrieve_users
from rest_framework.exceptions import APIException


def send_sse_event(event: EventCode, instance, data=None, exclude_myself=True):
    if data is None:
        data = {}
    kwargs = {}
    members = instance.place.participants
    if exclude_myself:
        members = members.exclude(id=instance.id)
    other_members = list(members.values_list('user_id', flat=True))
    if other_members:
        if event in (EventCode.LOBBY_UPDATE_PARTICIPANT, EventCode.LOBBY_LEAVE, EventCode.TOURNAMENT_LEAVE):
            data['id'] = instance.user_id
        if event in (EventCode.LOBBY_JOIN, EventCode.LOBBY_LEAVE, EventCode.LOBBY_MESSAGE, EventCode.TOURNAMENT_JOIN, EventCode.TOURNAMENT_LEAVE, EventCode.TOURNAMENT_MESSAGE):
            kwargs['username'] = instance.user_id
        if event in (EventCode.LOBBY_MESSAGE, EventCode.TOURNAMENT_MESSAGE):
            kwargs['message'] = data.pop('content')
        if event in (EventCode.LOBBY_JOIN, EventCode.TOURNAMENT_JOIN):
            user_instance = retrieve_users(instance.user_id)
            data.update(user_instance[0])
        create_sse_event(other_members, event, data=data, kwargs=kwargs)


def start_tournament_sse(instance):
    from tournament.serializers import TournamentSerializer

    try:
        create_sse_event(instance.users_id(), EventCode.TOURNAMENT_START, TournamentSerializer(instance).data, {'name': instance.name})
    except APIException:
        pass
