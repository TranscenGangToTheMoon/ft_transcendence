from lib_transcendence.services import create_sse_event
from lib_transcendence.sse_events import EventCode


def send_sse_event(event: EventCode, instance, data=None, exclude_myself=True):
    if data is None:
        data = {}
    kwargs = {}
    members = instance.place.participants
    if exclude_myself:
        members = members.exclude(id=instance.id)
    other_members = list(members.values_list('user_id', flat=True))
    if other_members:
        if event == EventCode.LOBBY_UPDATE_PARTICIPANT:
            data['id'] = instance.user_id
        else:
            kwargs['username'] = instance.user_id
        create_sse_event(other_members, event, data=data, kwargs=kwargs)
